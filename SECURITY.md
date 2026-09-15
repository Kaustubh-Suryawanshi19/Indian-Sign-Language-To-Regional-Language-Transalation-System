# Security Notes

## Credentials

The original development archive contained hard-coded Gemini and Roboflow credentials. The cleaned project removes them from source code and notebooks.

**Before publishing this cleaned repository, revoke/rotate every credential that appeared in the original archive or its Git history.**

Use `.env` locally:

```env
GEMINI_API_KEY=...
ROBOFLOW_API_KEY=...
```

Never commit `.env`.

## Web deployment

The Flask demo is designed for local use. Before exposing it to the internet:

- use a production WSGI server;
- restrict CORS to known origins;
- add authentication/authorization;
- add rate limiting for translation requests;
- add request-size and sequence validation;
- use browser camera capture instead of a server webcam;
- terminate TLS at the deployment boundary;
- monitor Gemini/API usage and failures.

## Reporting a vulnerability

Do not publish credentials, private datasets, or exploit details in a public issue. Rotate affected credentials first, then report the problem privately to the repository owner.
