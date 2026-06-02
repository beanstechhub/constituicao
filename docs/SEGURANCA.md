# Política de Segurança — constituicao.tech

## Reportar vulnerabilidade

Se você encontrou uma vulnerabilidade de segurança neste projeto, **NÃO abra issue pública**. Envie para: seguranca@constituicao.tech

Respondemos em até 72 horas.

## Escopo

Consideramos em escopo:
- Bypass de padrões de detecção (novo vetor não coberto)
- Vulnerabilidade na API (injection, SSRF, path traversal, etc.)
- Exposição de dados ou falha de privacidade
- Negação de serviço explorável

## Fora de escopo

- Falsos positivos/negativos previsíveis (use a tag `falso-positivo` em issues)
- Rate limiting funcionando como projetado
- Ataques que requerem acesso físico à infraestrutura

## Disclosure responsável

Após correção, o vetor será documentado publicamente (sem exploit code) no CHANGELOG com crédito ao pesquisador, a menos que prefira anonimato.
