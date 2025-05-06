# CDK Project

This project deploys an AWS Lambda function that is triggered every minute using an Amazon EventBridge rule.

## Deployment

1. Install dependencies:
   ```bash
   npm install
   ```

2. Build the project:
   ```bash
   npm run build
   ```
3. Bootstrap CDK (if not already done):
   ```bash 
   cdk bootstrap 
``

4. Synthesize the CloudFormation template:
   ```bash
   npm run cdk synth
   ```

5. Deploy the stack:
   ```bash
   npm run cdk deploy
   ```

6. Destroy the stack (if needed):
   ```bash
   npm run cdk destroy
   ```
