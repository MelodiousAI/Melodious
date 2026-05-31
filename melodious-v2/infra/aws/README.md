# AWS Public Demo Runbook

This runbook is the M6 deployment path for a low-cost public Melodious V2 demo. It is intentionally explicit about what is deployable now, what remains blocked without AWS resource values, and which limitations must be shown during the demo.

## Target Shape

- Backend: FastAPI container from `infra/docker/Dockerfile.api`.
- Container registry: Amazon ECR.
- Runtime: ECS Fargate or ECS Express Mode, one CPU task for the demo.
- Public API entrypoint: HTTPS Application Load Balancer or equivalent ECS-managed public endpoint.
- Frontend: Vite static build uploaded to private S3 bucket and served through CloudFront.
- Generated artifacts: served by the API artifact routes for the demo. The current service stores jobs in memory, so public demo transcriptions should be treated as short-lived.
- Model artifacts: kept private. Do not commit checkpoints, ONNX files, bucket names, presigned URLs, AWS account IDs, or `.env` files.

Do not use AWS App Runner for a new account. Project policy records that new App Runner customers stopped being accepted on April 30, 2026.

## Current Runtime Limits

- Uploaded images still use `heuristic_bootstrap`; do not present uploaded-image output as trained YOLOv8m detector quality.
- Sample transcriptions use the built-in V2 payload contract and can be used for public smoke testing.
- `MELODIOUS_GNN_CHECKPOINT` enables the legacy MUSCIMA GNN only if the checkpoint file is present inside the container or mounted volume.
- The Docker build does not copy ignored model artifacts. For the public demo, either mount/copy the private checkpoint to the configured path or leave GNN unset and show the explicit fallback metadata.
- `MELODIOUS_CORS_ORIGINS` must include the CloudFront frontend origin or browser calls from the frontend will fail CORS.

## Local Prerequisite Checks

Run these before changing AWS resources:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe -m unittest discover tests
..\.venv\Scripts\python.exe scripts\validate_metric_claims.py
..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --local-testclient --output runs\deploy\m6_local_smoke\smoke.json
```

Expected smoke coverage:

- `GET /health` returns `status = ok`.
- `GET /version` returns schema version `2.0`.
- `GET /samples` returns at least one sample.
- `POST /transcriptions` completes for `sample-notation-1`.
- MusicXML and MIDI artifact downloads return HTTP 200 and non-empty bytes.

## Backend Build And Push

Use local environment variables instead of committing account-specific values:

```powershell
$env:AWS_REGION='us-east-1'
$env:ECR_REPOSITORY='melodious-v2-api'
$env:IMAGE_TAG='m6-demo'

aws sts get-caller-identity
aws ecr create-repository --repository-name $env:ECR_REPOSITORY --region $env:AWS_REGION
$accountId = aws sts get-caller-identity --query Account --output text
$imageUri = "$accountId.dkr.ecr.$env:AWS_REGION.amazonaws.com/$env:ECR_REPOSITORY:$env:IMAGE_TAG"
aws ecr get-login-password --region $env:AWS_REGION | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$env:AWS_REGION.amazonaws.com"
docker build -f infra/docker/Dockerfile.api -t "melodious-v2-api:$env:IMAGE_TAG" .
docker tag "melodious-v2-api:$env:IMAGE_TAG" $imageUri
docker push $imageUri
```

Do not paste `$accountId` or `$imageUri` into committed docs.

## ECS Task Definition

Copy `infra/aws/task-definition.template.json` to ignored generated state and replace placeholders locally:

```powershell
New-Item -ItemType Directory -Force infra\aws\generated | Out-Null
Copy-Item infra\aws\task-definition.template.json infra\aws\generated\task-definition.json
notepad infra\aws\generated\task-definition.json
```

Replace these values in `infra\aws\generated\task-definition.json`:

- `REPLACE_WITH_EXECUTION_ROLE_ARN`
- `REPLACE_WITH_TASK_ROLE_ARN`
- `REPLACE_WITH_ECR_IMAGE_URI`
- `REPLACE_WITH_REGION`
- `https://REPLACE_WITH_CLOUDFRONT_DOMAIN`
- `MELODIOUS_GNN_CHECKPOINT` path if a private checkpoint is mounted somewhere other than `/app/artifacts/graph/gnn_checkpoint.pt`

Register the task:

```powershell
aws logs create-log-group --log-group-name /ecs/melodious-v2-api --region $env:AWS_REGION
aws ecs register-task-definition --cli-input-json file://infra/aws/generated/task-definition.json --region $env:AWS_REGION
```

## ECS Service

Create or update one public demo service. The exact subnet, security group, listener, and target group values must come from the AWS account and must not be committed.

Minimum security-group rules:

- ALB allows public HTTPS 443.
- ALB forwards to the ECS target group on container port 8000.
- ECS task security group allows inbound 8000 only from the ALB security group.
- ECS task has outbound HTTPS for logs and any private artifact fetch.

Create service after the task definition is registered:

```powershell
aws ecs create-cluster --cluster-name melodious-v2-demo --region $env:AWS_REGION
aws ecs create-service `
  --cluster melodious-v2-demo `
  --service-name melodious-v2-api `
  --task-definition melodious-v2-api `
  --desired-count 1 `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[subnet-REPLACE],securityGroups=[sg-REPLACE],assignPublicIp=ENABLED}" `
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:REGION:ACCOUNT:targetgroup/REPLACE,containerName=api,containerPort=8000" `
  --region $env:AWS_REGION
```

If the service already exists, deploy a new task definition revision:

```powershell
aws ecs update-service --cluster melodious-v2-demo --service melodious-v2-api --task-definition melodious-v2-api --force-new-deployment --region $env:AWS_REGION
aws ecs wait services-stable --cluster melodious-v2-demo --services melodious-v2-api --region $env:AWS_REGION
```

## Frontend Build And Publish

Build with the public API URL, then sync only the generated `dist` folder:

```powershell
cd frontend
$env:VITE_API_BASE_URL='https://REPLACE_WITH_PUBLIC_API_HOST'
npm run build
aws s3 sync dist "s3://REPLACE_WITH_FRONTEND_BUCKET/" --delete --region $env:AWS_REGION
aws cloudfront create-invalidation --distribution-id REPLACE_WITH_DISTRIBUTION_ID --paths "/*"
cd ..
```

The CloudFront domain used here must also be included in `MELODIOUS_CORS_ORIGINS` for the API task.

## Public Smoke Test

Python smoke tester:

```powershell
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --api-base-url https://REPLACE_WITH_PUBLIC_API_HOST --output runs\deploy\m6_public_smoke\smoke.json
```

PowerShell smoke tester:

```powershell
.\infra\aws\smoke_test.ps1 -ApiBaseUrl https://REPLACE_WITH_PUBLIC_API_HOST -OutputPath runs\deploy\m6_public_smoke\smoke.ps1.json
```

The smoke output is deployment evidence. It should remain under ignored `runs\deploy\...` unless a final grading artifact intentionally summarizes it.

Manual frontend smoke:

- Open the CloudFront URL.
- Run the sample transcription.
- Download the MusicXML artifact.
- Download the MIDI artifact.
- Confirm the result panel shows detector mode and assembly fallback metadata.

## Cost Control And Shutdown

Use one task while demoing:

```powershell
aws ecs update-service --cluster melodious-v2-demo --service melodious-v2-api --desired-count 1 --region $env:AWS_REGION
```

Scale to zero immediately after the demo:

```powershell
aws ecs update-service --cluster melodious-v2-demo --service melodious-v2-api --desired-count 0 --region $env:AWS_REGION
```

Optional cleanup after grading:

```powershell
aws ecs delete-service --cluster melodious-v2-demo --service melodious-v2-api --force --region $env:AWS_REGION
aws ecs delete-cluster --cluster melodious-v2-demo --region $env:AWS_REGION
aws ecr delete-repository --repository-name melodious-v2-api --force --region $env:AWS_REGION
aws cloudfront create-invalidation --distribution-id REPLACE_WITH_DISTRIBUTION_ID --paths "/*"
aws s3 rm "s3://REPLACE_WITH_FRONTEND_BUCKET/" --recursive --region $env:AWS_REGION
```

Keep the S3 bucket and CloudFront distribution only if they are reused for final presentation.

## Current Blocker To Actual Public Deploy

This repository now has the deployable container, task template, CORS configuration, frontend build path, and smoke tooling. An actual AWS deploy still requires account-local values that cannot be inferred or committed:

- AWS profile or OIDC role access.
- Region.
- ECR repository permission.
- ECS execution role ARN.
- ECS task role ARN.
- VPC subnet IDs.
- Security group IDs.
- ALB target group and listener.
- S3 frontend bucket.
- CloudFront distribution ID and domain.

Exact next action when those values are available:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --local-testclient --output runs\deploy\m6_local_smoke\smoke.json
```

Then run the Backend Build And Push, ECS Task Definition, ECS Service, Frontend Build And Publish, and Public Smoke Test sections above.
