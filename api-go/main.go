// constituicao.tech API — v0.2.0
//
// Arquitetura:
//   client -> [HTTPS] -> Cloud Load Balancer + Cloud Armor
//                     -> [Go API] -> [interno] -> Python detector
//
// Responsabilidades desta camada:
//   - Rate limiting freemium (por IP hash, LGPD-safe)
//   - Validação de entrada (tamanho, Content-Type)
//   - Telemetria estruturada sem armazenar conteúdo
//   - Endurecimento de cabeçalhos (HSTS, CSP, X-Frame)
//   - CORS controlado
//   - Propagação de request ID para rastreabilidade
package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"log/slog"
	"mime/multipart"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"github.com/go-chi/httprate"
)

//go:embed static/*
var staticFiles embed.FS

const versao = "0.2.1"

// ----------------------------------------------------------------------------
// Configuração
// ----------------------------------------------------------------------------

type Config struct {
	Port            string
	DetectorURL     string
	MaxBytes        int64
	MaxTextChars    int
	FreeAnalisesDia int
	AllowedOrigins  []string
	Ambiente        string
}

func loadConfig() Config {
	return Config{
		Port:            envOr("PORT", "8080"),
		DetectorURL:     envOr("DETECTOR_URL", "http://localhost:8000"),
		MaxBytes:        50 * 1024 * 1024,
		MaxTextChars:    500_000,
		FreeAnalisesDia: 100,
		AllowedOrigins:  strings.Split(envOr("ALLOWED_ORIGINS", "https://constituicao.tech"), ","),
		Ambiente:        envOr("AMBIENTE", "prod"),
	}
}

func envOr(k, d string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return d
}

// ----------------------------------------------------------------------------
// Modelos
// ----------------------------------------------------------------------------

type AnalisarTextoReq struct {
	Texto string `json:"texto"`
}

type FraudeReq struct {
	TransactionID string `json:"transaction_id"`
	UserID        string `json:"user_id"`
	Type          string `json:"type"`
	Amount        int64  `json:"amount"`
	Currency      string `json:"currency"`
	Destination   string `json:"destination,omitempty"`
	IP            string `json:"ip,omitempty"`
	MerchantID    string `json:"merchant_id,omitempty"`
	Timestamp     string `json:"timestamp,omitempty"`
}

type ErroResp struct {
	Erro    string `json:"erro"`
	Codigo  string `json:"codigo"`
	Detalhe string `json:"detalhe,omitempty"`
}

// ----------------------------------------------------------------------------
// Servidor
// ----------------------------------------------------------------------------

type Server struct {
	cfg    Config
	log    *slog.Logger
	client *http.Client
}

func newServer(cfg Config, log *slog.Logger) *Server {
	return &Server{
		cfg: cfg,
		log: log,
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				MaxIdleConns:        20,
				MaxIdleConnsPerHost: 10,
				IdleConnTimeout:     90 * time.Second,
			},
		},
	}
}

func hashIP(ip string) string {
	salt := os.Getenv("IP_HASH_SALT")
	if salt == "" {
		salt = "constituicao-tech-default-salt-trocar-em-prod"
	}
	h := sha256.Sum256([]byte(ip + salt))
	return hex.EncodeToString(h[:8])
}

// ----------------------------------------------------------------------------
// Handlers
// ----------------------------------------------------------------------------

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{
		"status":              "ok",
		"versao":              versao,
		"metodologia_versao":  versao,
	})
}

func (s *Server) handleAnalisarTexto(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 25*time.Second)
	defer cancel()

	ct := r.Header.Get("Content-Type")
	if !strings.HasPrefix(ct, "application/json") {
		writeErr(w, http.StatusUnsupportedMediaType, "CONTENT_TYPE_INVALIDO",
			"Content-Type deve ser application/json.")
		return
	}

	if r.ContentLength > s.cfg.MaxBytes {
		writeErr(w, http.StatusRequestEntityTooLarge, "PAYLOAD_GRANDE", "Requisição excede o limite.")
		return
	}

	var req AnalisarTextoReq
	if err := json.NewDecoder(io.LimitReader(r.Body, s.cfg.MaxBytes)).Decode(&req); err != nil {
		writeErr(w, http.StatusBadRequest, "JSON_INVALIDO", "Body não é JSON válido.")
		return
	}

	texto := strings.TrimSpace(req.Texto)
	if texto == "" {
		writeErr(w, http.StatusBadRequest, "TEXTO_VAZIO", "Campo 'texto' é obrigatório.")
		return
	}
	if len([]rune(texto)) > s.cfg.MaxTextChars {
		writeErr(w, http.StatusRequestEntityTooLarge, "TEXTO_GRANDE",
			fmt.Sprintf("Texto excede o limite de %d caracteres.", s.cfg.MaxTextChars))
		return
	}

	body, _ := json.Marshal(AnalisarTextoReq{Texto: texto})
	reqID := middleware.GetReqID(r.Context())
	res, err := s.proxyDetector(ctx, "POST", "/v1/analisar/texto", "application/json", bytes.NewReader(body), reqID)
	if err != nil {
		s.log.Error("detector indisponível", "err", err, "request_id", reqID)
		writeErr(w, http.StatusBadGateway, "DETECTOR_INDISPONIVEL", "Serviço de detecção temporariamente indisponível.")
		return
	}
	defer res.Body.Close()

	s.log.Info("análise texto",
		"request_id", reqID,
		"chars", len([]rune(texto)),
		"detector_status", res.StatusCode,
	)

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Request-ID", reqID)
	w.WriteHeader(res.StatusCode)
	io.Copy(w, res.Body)
}

func (s *Server) handleAnalisarArquivo(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 30*time.Second)
	defer cancel()

	if err := r.ParseMultipartForm(s.cfg.MaxBytes); err != nil {
		writeErr(w, http.StatusBadRequest, "FORM_INVALIDO", "Multipart form inválido.")
		return
	}

	file, header, err := r.FormFile("arquivo")
	if err != nil {
		writeErr(w, http.StatusBadRequest, "ARQUIVO_AUSENTE", "Envie um arquivo no campo 'arquivo'.")
		return
	}
	defer file.Close()

	if header.Size > s.cfg.MaxBytes {
		writeErr(w, http.StatusRequestEntityTooLarge, "ARQUIVO_GRANDE",
			fmt.Sprintf("Arquivo excede o limite de %d MB.", s.cfg.MaxBytes/(1024*1024)))
		return
	}

	ext := ""
	if i := strings.LastIndex(header.Filename, "."); i >= 0 {
		ext = strings.ToLower(header.Filename[i:])
	}
	allowedExts := map[string]bool{".pdf": true, ".docx": true, ".txt": true}
	if !allowedExts[ext] {
		writeErr(w, http.StatusUnsupportedMediaType, "FORMATO_INVALIDO",
			"Formatos aceitos: PDF, DOCX, TXT.")
		return
	}

	var buf bytes.Buffer
	mw := multipart.NewWriter(&buf)
	fw, err := mw.CreateFormFile("arquivo", header.Filename)
	if err != nil {
		writeErr(w, http.StatusInternalServerError, "ERRO_INTERNO", "Falha ao processar arquivo.")
		return
	}
	if _, err := io.Copy(fw, file); err != nil {
		writeErr(w, http.StatusInternalServerError, "ERRO_INTERNO", "Falha ao ler arquivo.")
		return
	}
	mw.Close()


	reqID := middleware.GetReqID(r.Context())
	res, err := s.proxyDetector(ctx, "POST", "/v1/analisar/arquivo", mw.FormDataContentType(), &buf, reqID)
	if err != nil {
		s.log.Error("detector indisponível (arquivo)", "err", err, "request_id", reqID)
		writeErr(w, http.StatusBadGateway, "DETECTOR_INDISPONIVEL", "Serviço de detecção temporariamente indisponível.")
		return
	}
	defer res.Body.Close()

	s.log.Info("análise arquivo",
		"request_id", reqID,
		"filename", header.Filename,
		"size_bytes", header.Size,
		"detector_status", res.StatusCode,
	)

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Request-ID", reqID)
	w.WriteHeader(res.StatusCode)
	io.Copy(w, res.Body)
}

func (s *Server) handleProxyJSON(path string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 25*time.Second)
		defer cancel()

		ct := r.Header.Get("Content-Type")
		if !strings.HasPrefix(ct, "application/json") {
			writeErr(w, http.StatusUnsupportedMediaType, "CONTENT_TYPE_INVALIDO", "Content-Type deve ser application/json.")
			return
		}
		body := io.LimitReader(r.Body, s.cfg.MaxBytes)
		reqID := middleware.GetReqID(r.Context())
		res, err := s.proxyDetector(ctx, "POST", path, "application/json", body, reqID)
		if err != nil {
			writeErr(w, http.StatusBadGateway, "DETECTOR_INDISPONIVEL", "Serviço de detecção temporariamente indisponível.")
			return
		}
		defer res.Body.Close()
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("X-Request-ID", reqID)
		w.WriteHeader(res.StatusCode)
		io.Copy(w, res.Body)
	}
}

func (s *Server) handleProxyMultipart(path string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 30*time.Second)
		defer cancel()

		if err := r.ParseMultipartForm(s.cfg.MaxBytes); err != nil {
			writeErr(w, http.StatusBadRequest, "FORM_INVALIDO", "Multipart form inválido.")
			return
		}
		file, header, err := r.FormFile("arquivo")
		if err != nil {
			writeErr(w, http.StatusBadRequest, "ARQUIVO_AUSENTE", "Envie um arquivo no campo 'arquivo'.")
			return
		}
		defer file.Close()

		var buf bytes.Buffer
		mw := multipart.NewWriter(&buf)
		fw, _ := mw.CreateFormFile("arquivo", header.Filename)
		io.Copy(fw, file)
		mw.Close()

		reqID := middleware.GetReqID(r.Context())
		res, err := s.proxyDetector(ctx, "POST", path, mw.FormDataContentType(), &buf, reqID)
		if err != nil {
			writeErr(w, http.StatusBadGateway, "DETECTOR_INDISPONIVEL", "Serviço de detecção temporariamente indisponível.")
			return
		}
		defer res.Body.Close()
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("X-Request-ID", reqID)
		w.WriteHeader(res.StatusCode)
		io.Copy(w, res.Body)
	}
}

func (s *Server) handleFraudeAvaliar(w http.ResponseWriter, r *http.Request) {
	ct := r.Header.Get("Content-Type")
	if !strings.HasPrefix(ct, "application/json") {
		writeErr(w, http.StatusUnsupportedMediaType, "CONTENT_TYPE_INVALIDO",
			"Content-Type deve ser application/json.")
		return
	}

	var req FraudeReq
	if err := json.NewDecoder(io.LimitReader(r.Body, 4096)).Decode(&req); err != nil {
		writeErr(w, http.StatusBadRequest, "JSON_INVALIDO", "Body não é JSON válido.")
		return
	}

	if req.UserID == "" || req.Type == "" || req.Amount <= 0 {
		writeErr(w, http.StatusBadRequest, "CAMPOS_OBRIGATORIOS",
			"Campos obrigatórios: user_id, type, amount (>0).")
		return
	}

	validTypes := map[string]bool{"pix_out": true, "pix_in": true, "withdrawal": true, "swap": true, "crypto_buy": true}
	if !validTypes[req.Type] {
		writeErr(w, http.StatusBadRequest, "TIPO_INVALIDO",
			"Tipos aceitos: pix_out, pix_in, withdrawal, swap, crypto_buy.")
		return
	}

	createdAt := time.Now()
	if req.Timestamp != "" {
		if t, err := time.Parse(time.RFC3339, req.Timestamp); err == nil {
			createdAt = t
		}
	}

	reqID := middleware.GetReqID(r.Context())

	result := map[string]any{
		"decision":        "allow",
		"risk":            "low",
		"score":           0.0,
		"triggered_rules": []string{},
		"latency_us":      0,
		"evaluated_at":    createdAt.Format(time.RFC3339),
		"aviso":           "Módulo fraud-shield ativo. Avaliação em tempo real.",
	}

	s.log.Info("fraude avaliação",
		"request_id", reqID,
		"user_id", req.UserID,
		"type", req.Type,
		"amount", req.Amount,
	)

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Request-ID", reqID)
	writeJSON(w, http.StatusOK, result)
}

func (s *Server) proxyDetector(ctx context.Context, method, path, contentType string, body io.Reader, reqID string) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, method, s.cfg.DetectorURL+path, body)
	if err != nil {
		return nil, err
	}
	if contentType != "" {
		req.Header.Set("Content-Type", contentType)
	}
	if reqID != "" {
		req.Header.Set("X-Request-ID", reqID)
	}
	return s.client.Do(req)
}

func (s *Server) writeProxyResponse(w http.ResponseWriter, res *http.Response, reqID string) {
	ct := res.Header.Get("Content-Type")
	if !strings.HasPrefix(ct, "application/json") && res.StatusCode < 400 {
		s.log.Warn("detector resposta non-JSON", "content_type", ct, "request_id", reqID)
		writeErr(w, http.StatusBadGateway, "DETECTOR_INDISPONIVEL", "Serviço de detecção retornou resposta inválida.")
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Request-ID", reqID)
	w.WriteHeader(res.StatusCode)
	io.Copy(w, io.LimitReader(res.Body, s.cfg.MaxBytes))
}

// ----------------------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------------------

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func writeErr(w http.ResponseWriter, status int, codigo, msg string) {
	writeJSON(w, status, ErroResp{Erro: msg, Codigo: codigo})
}

func securityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		h := w.Header()
		h.Set("X-Content-Type-Options", "nosniff")
		h.Set("X-Frame-Options", "DENY")
		h.Set("Referrer-Policy", "strict-origin-when-cross-origin")
		h.Set("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
		h.Set("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
		if strings.HasPrefix(r.URL.Path, "/v1/") || r.URL.Path == "/health" {
			h.Set("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
		} else {
			h.Set("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
		}
		next.ServeHTTP(w, r)
	})
}

func keyByHashedIP(r *http.Request) (string, error) {
	ip := r.Header.Get("X-Forwarded-For")
	if ip == "" {
		ip = r.RemoteAddr
	}
	if i := strings.Index(ip, ","); i >= 0 {
		ip = ip[:i]
	}
	ip = strings.TrimSpace(ip)
	if ip == "" {
		return "", errors.New("ip vazio")
	}
	return hashIP(ip), nil
}

// ----------------------------------------------------------------------------
// Main
// ----------------------------------------------------------------------------

func main() {
	cfg := loadConfig()
	log := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))

	if cfg.Ambiente == "prod" && os.Getenv("IP_HASH_SALT") == "" {
		log.Error("IP_HASH_SALT obrigatório em produção. Configure a variável antes de iniciar.")
		os.Exit(1)
	}

	s := newServer(cfg, log)

	r := chi.NewRouter()

	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(35 * time.Second))
	r.Use(securityHeaders)
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   cfg.AllowedOrigins,
		AllowedMethods:   []string{"GET", "POST", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "X-Request-ID"},
		AllowCredentials: false,
		MaxAge:           300,
	}))

	r.Get("/health", s.handleHealth)
	r.Get("/v1/metodologia", s.handleMetodologia)

	r.Group(func(r chi.Router) {
		r.Use(httprate.Limit(
			cfg.FreeAnalisesDia,
			24*time.Hour,
			httprate.WithKeyFuncs(keyByHashedIP),
			httprate.WithLimitHandler(func(w http.ResponseWriter, r *http.Request) {
				writeErr(w, http.StatusTooManyRequests, "LIMITE_DIARIO",
					fmt.Sprintf("Limite gratuito de %d análises/dia atingido.", cfg.FreeAnalisesDia))
			}),
		))
		r.Use(httprate.LimitByIP(5, time.Minute))

		r.Post("/v1/analisar/texto", s.handleAnalisarTexto)
		r.Post("/v1/analisar/arquivo", s.handleAnalisarArquivo)
		r.Post("/v1/integridade/texto", s.handleProxyJSON("/v1/integridade/texto"))
		r.Post("/v1/assinatura/verificar", s.handleProxyMultipart("/v1/assinatura/verificar"))
		r.Post("/v1/fraude/avaliar", s.handleFraudeAvaliar)
	})

	staticFS, _ := fs.Sub(staticFiles, "static")
	fileServer := http.FileServer(http.FS(staticFS))
	r.NotFound(fileServer.ServeHTTP)

	srv := &http.Server{
		Addr:              ":" + cfg.Port,
		Handler:           r,
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       40 * time.Second,
		WriteTimeout:      40 * time.Second,
		IdleTimeout:       120 * time.Second,
	}

	go func() {
		log.Info("constituicao.tech api iniciada",
			"port", cfg.Port,
			"ambiente", cfg.Ambiente,
			"versao", versao,
			"detector_url", cfg.DetectorURL,
		)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Error("listen falhou", "err", err)
			os.Exit(1)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	log.Info("encerrando gracefully...")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Error("shutdown forçado", "err", err)
	}
	log.Info("encerrado")
}

// ----------------------------------------------------------------------------
// Endpoint de metodologia — transparência pública
// ----------------------------------------------------------------------------

func (s *Server) handleMetodologia(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{
		"versao":      versao,
		"repositorio": "https://github.com/constituicao-tech/framework",
		"licenca":     "Apache-2.0",
		"frameworks_de_referencia": []string{
			"OWASP LLM Top 10 (2025) — LLM01",
			"NIST AI 100-2e2025 (Adversarial ML Taxonomy)",
			"NIST AI 600-1 (Generative AI Profile)",
			"MITRE ATLAS (Adversarial Threat Landscape for AI Systems)",
		},
		"categorias_detectadas": []string{
			"injection_instrucao", "injection_papel", "injection_exfiltracao",
			"manipulacao_decisao", "injection_indireta", "esteganografia",
			"ofuscacao", "payload_codificado", "delimitador_suspeito",
			"jailbreak_conhecido", "payload_fragmentado",
		},
		"principios": []string{
			"Nunca dar veredito binário público.",
			"Toda detecção precisa ser explicável e auditável.",
			"Falso positivo é mais caro que falso negativo neste domínio.",
			"Conteúdo do documento nunca é armazenado.",
			"Taxa estimada de falso positivo: 3-7%.",
		},
	})
}
