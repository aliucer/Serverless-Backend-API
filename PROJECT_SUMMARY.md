# My Serverless Backend Project - Ali Ucer

## What This Is

This is my personal project building a production-ready serverless backend on AWS. I built it to learn modern cloud architecture and showcase what I can do with AWS services.

## The Story

I started this project because I wanted to understand:
1. How do you build scalable APIs without managing servers?
2. What's the big deal with serverless architecture?
3. How do you actually use AWS services in a real project?

Turns out, building this taught me way more than I expected. I learned about:
- DynamoDB schema design (those GSIs were confusing at first!)
- Infrastructure as Code with SAM templates
- CI/CD with GitHub Actions
- Best practices like idempotency and retry logic
- Debugging production issues in CloudWatch (not fun, but essential)

## What I Built

### The API
A REST API with two main parts:
- **Users API**: Create, read, update, delete users
- **Assets API**: Handle file uploads to S3

Both implemented in **Python and TypeScript** because I wanted to show I can work with both.

### Key Features
✅ REST endpoints on API Gateway  
✅ DynamoDB with proper schema design  
✅ S3 for file storage with presigned URLs  
✅ CloudWatch logging and monitoring  
✅ Retry logic with exponential backoff  
✅ Idempotency (no duplicate operations)  
✅ CI/CD pipeline  
✅ Unit and integration tests  

## Technical Highlights

### DynamoDB Schema
I spent a lot of time getting this right:
- Partition keys for fast lookups
- GSIs (Global Secondary Indexes) for different query patterns
- TTL (Time To Live) for automatic cleanup
- Conditional writes to prevent duplicate records

### Why Both Python and TypeScript?
Python's been my primary language, but I wanted to learn TypeScript too. This was the perfect project to implement both and compare them. Spoiler: they both work well for serverless!

### The CI/CD Part
This was honestly one of the hardest but most rewarding parts. Getting GitHub Actions to automatically test and deploy took me a whole weekend, but now every push to main deploys to AWS automatically. So cool!

## What I Learned

### The Good
- Serverless architecture is genuinely powerful
- CloudWatch is essential for debugging production issues
- Infrastructure as Code saves hours of manual setup
- Testing saves you from production fires

### The Challenges
- Cold starts in Lambda can be slow during development
- DynamoDB pricing model took research to understand
- SAM templates have a learning curve
- S3 presigned URLs were tricky to implement correctly

### Skills Gained
- AWS Lambda, API Gateway, DynamoDB, S3
- Infrastructure as Code (AWS SAM)
- CloudWatch for monitoring and debugging
- GitHub Actions for CI/CD
- Testing strategies for serverless functions
- Best practices for production serverless apps

## Project Stats

- **Time**: Started in late 2023, still maintaining it
- **Lines of Code**: ~2500+
- **Files**: 30+ files
- **Languages**: Python, TypeScript, YAML
- **AWS Services**: Lambda, API Gateway, DynamoDB, S3, CloudWatch
- **Cost**: Under $1/month for normal usage (thanks free tier!)

## Why This Matters

This project demonstrates:
- I can build production-ready software
- I understand AWS serverless architecture
- I can write clean, tested code
- I know how to set up CI/CD pipelines
- I understand cloud security and best practices

## Current Status

✅ Fully functional API  
✅ Deployed to AWS  
✅ Tests passing  
✅ CI/CD working  
✅ Documentation complete  

**Future ideas** (if I have time):
- Add authentication with AWS Cognito
- Implement GraphQL endpoint
- Add real-time features
- Multi-region deployment

## For Employers/Recruiters

This project represents what I can do when I'm given the freedom to learn and build. It's not just a demo - it's a working API with proper architecture, testing, monitoring, and documentation.

Want to see it in action? Check the deployment instructions in the README!

- Ali Ucer
