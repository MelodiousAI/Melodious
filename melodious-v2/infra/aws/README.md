# AWS Deployment

Target deployment:

- Backend: FastAPI container on ECS Express Mode or ECS Fargate.
- Container registry: Amazon ECR.
- Frontend: static Vite build on S3 + CloudFront.
- Artifacts/uploads: private S3 bucket with short-lived presigned URLs.
- Logs: CloudWatch.
- CI/CD: GitHub Actions OIDC, no committed AWS keys.

## Why Not App Runner

Do not use App Runner for a new account. AWS states that App Runner stopped accepting new customers starting April 30, 2026. Use ECS Express Mode or ECS Fargate instead.

## Required GitHub Secrets / Variables

Use repository variables where possible:

- `AWS_REGION`
- `AWS_ROLE_TO_ASSUME`
- `ECR_REPOSITORY`
- `ECS_CLUSTER`
- `ECS_SERVICE`
- `S3_FRONTEND_BUCKET`
- `CLOUDFRONT_DISTRIBUTION_ID`

Do not store static AWS access keys.

## Smoke Test

After deployment:

```powershell
Invoke-RestMethod https://YOUR_API_HOST/health
Invoke-RestMethod https://YOUR_API_HOST/version
```

Then open the CloudFront frontend and run one sample transcription plus one upload transcription.

