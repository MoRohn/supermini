# GitHub Repository Setup Guide

This guide provides step-by-step instructions for configuring the SuperMini GitHub repository for professional open-source development, including branch protection, automated workflows, and community features.

## Table of Contents

- [Repository Configuration](#repository-configuration)
- [Branch Protection Rules](#branch-protection-rules)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Community Features](#community-features)
- [Security Settings](#security-settings)
- [Autonomous Enhancement Integration](#autonomous-enhancement-integration)
- [Release Management](#release-management)

## Repository Configuration

### 1. Basic Repository Settings

#### Repository Details
```
Repository Name: supermini
Description: A powerful desktop AI assistant with autonomous enhancement capabilities
Website: https://github.com/rohnspringfield/supermini
Topics: ai, desktop-app, pyqt6, claude-api, ollama, autonomous-ai, python
```

#### Visibility Settings
- **Public Repository**: Enable public access for open-source contributions
- **Include in search**: Allow repository to appear in search results
- **Restrict pushes**: Limit push access to collaborators and organization members

#### Features Configuration
```yaml
Features:
  - ✅ Issues
  - ✅ Pull requests
  - ✅ Wiki (for extended documentation)
  - ✅ Discussions (for community Q&A)
  - ✅ Projects (for roadmap management)
  - ✅ Actions (for CI/CD automation)
  - ✅ Security (for vulnerability reporting)
  - ✅ Insights (for analytics)
```

### 2. Repository Settings

#### General Settings
- **Default branch**: `main`
- **Allow merge commits**: ✅ Enabled
- **Allow squash merging**: ✅ Enabled
- **Allow rebase merging**: ✅ Enabled
- **Automatically delete head branches**: ✅ Enabled

#### Pull Request Settings
- **Allow auto-merge**: ✅ Enabled
- **Require status checks**: ✅ Enabled
- **Require up-to-date branches**: ✅ Enabled
- **Suggest updating PR branches**: ✅ Enabled

## Branch Protection Rules

### Main Branch Protection

Configure branch protection for the `main` branch:

#### Required Status Checks
```yaml
Status Checks:
  - ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  
Required Checks:
  - ci/test-suite (Linux, macOS, Windows)
  - ci/security-scan
  - ci/code-quality
  - ci/integration-tests
  - ci/autonomous-safety-tests
```

#### Branch Restrictions
```yaml
Restrictions:
  - ✅ Restrict pushes that create files
  - ✅ Require pull request reviews before merging
  - Require 2 reviews from code owners
  - ✅ Dismiss stale reviews when new commits are pushed
  - ✅ Require review from CODEOWNERS
  - ✅ Include administrators (maintainers must follow rules)
```

#### Additional Protection
```yaml
Additional Rules:
  - ✅ Require signed commits
  - ✅ Require linear history
  - ✅ Allow force pushes: Never
  - ✅ Allow deletions: Never
  - ✅ Restrict pushes that create files: Enabled
```

### Development Branch Protection

For `develop` branch (if used):

```yaml
Development Branch:
  - ✅ Require pull request reviews (1 reviewer minimum)
  - ✅ Require status checks
  - Allow force pushes for maintainers
  - Allow branch deletion after merge
```

## GitHub Actions Workflows

### 1. Continuous Integration Workflow

The existing `.github/workflows/ci.yml` provides:

```yaml
Trigger Events:
  - push: [main, develop]
  - pull_request: [main]

Test Matrix:
  - OS: [ubuntu-latest, macos-latest, windows-latest]
  - Python: [3.9, 3.10, 3.11, 3.12]

Quality Checks:
  - Code linting (flake8, black, isort)
  - Security scanning (bandit, safety)
  - Test coverage (pytest with coverage)
  - Integration tests
  - Autonomous safety tests
```

### 2. Release Workflow

The `.github/workflows/release.yml` handles:

```yaml
Release Automation:
  - Automatic release creation on version tags
  - Multi-platform build artifacts
  - Release note generation from CHANGELOG.md
  - Asset uploading (binaries, packages)
  - Notification to community channels
```

### 3. Additional Recommended Workflows

#### Dependency Update Workflow
```yaml
# .github/workflows/dependency-update.yml
name: Dependency Updates
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
jobs:
  update-dependencies:
    runs-on: ubuntu-latest
    steps:
      - name: Check for updates
        uses: actions/setup-python@v4
      - name: Create PR for updates
        uses: peter-evans/create-pull-request@v5
```

#### Stale Issue Management
```yaml
# .github/workflows/stale.yml
name: Mark stale issues and PRs
on:
  schedule:
    - cron: '0 0 * * *'  # Daily
jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v8
        with:
          stale-issue-message: 'This issue has been automatically marked as stale.'
          days-before-stale: 60
          days-before-close: 7
```

## Community Features

### 1. Issue Templates

Existing templates in `.github/ISSUE_TEMPLATE/`:

- `bug_report.yml`: Structured bug reporting
- `feature_request.yml`: Feature suggestion template

### 2. Pull Request Template

The `.github/pull_request_template.md` provides:

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Autonomous enhancement

## Testing
- [ ] Tests pass locally
- [ ] Added/updated tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
```

### 3. Discussion Categories

Configure GitHub Discussions with these categories:

```yaml
Categories:
  - 📢 Announcements: Official project announcements
  - 💡 Ideas: Feature suggestions and brainstorming
  - 🙋 Q&A: Questions and help requests
  - 🗣️ General: General project discussion
  - 🤖 Autonomous AI: Discussion about AI contributions
  - 🛠️ Development: Technical development discussions
  - 🐛 Troubleshooting: Help with issues and problems
```

### 4. Project Boards

Create project boards for:

#### Roadmap Board
```yaml
Columns:
  - 📋 Backlog: Future features and improvements
  - 🎯 Planned: Items planned for upcoming releases
  - 🔄 In Progress: Currently being worked on
  - 👀 In Review: Pending review/testing
  - ✅ Completed: Finished items
```

#### Bug Tracking Board
```yaml
Columns:
  - 🐛 Reported: New bug reports
  - 🔍 Investigating: Bugs being investigated
  - 🛠️ Fixing: Bugs being fixed
  - 🧪 Testing: Fixes being tested
  - ✅ Resolved: Fixed bugs
```

## Security Settings

### 1. Security Policies

- **SECURITY.md**: Already configured in `.github/SECURITY.md`
- **Private vulnerability reporting**: Enable in repository settings
- **Security advisories**: Configure for coordinated disclosure

### 2. Dependency Scanning

Configure Dependabot in `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "maintainer-username"
    assignees:
      - "maintainer-username"
```

### 3. Code Scanning

Enable GitHub CodeQL scanning:

```yaml
# .github/workflows/codeql-analysis.yml
name: CodeQL Analysis
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  analyze:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        language: ['python']
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v2
      - uses: github/codeql-action/analyze@v2
```

## Autonomous Enhancement Integration

### 1. GitHub App Authentication

For autonomous enhancements, configure GitHub App or Personal Access Token:

#### Using GitHub App (Recommended)
```bash
# Create GitHub App with permissions:
# - Contents: Read & Write
# - Pull requests: Read & Write
# - Issues: Read & Write
# - Metadata: Read

# Set environment variables:
export GITHUB_APP_ID="your-app-id"
export GITHUB_APP_PRIVATE_KEY="path-to-private-key.pem"
export GITHUB_INSTALLATION_ID="installation-id"
```

#### Using Personal Access Token
```bash
# Create token with scopes:
# - repo (full control)
# - workflow
# - write:packages

export GITHUB_TOKEN="ghp_your-token-here"
```

### 2. Autonomous Enhancement Configuration

Repository settings for autonomous contributions:

```yaml
# .github/autonomous-config.yml
autonomous_enhancement:
  enabled: true
  max_prs_per_day: 3
  auto_merge: false
  require_human_review: true
  
  allowed_file_patterns:
    - "*.py"
    - "*.md"
    - "*.yml"
    - "*.yaml"
    - "requirements*.txt"
  
  restricted_patterns:
    - ".github/workflows/*"
    - "security/*"
    - "*.key"
    - "*.env"
  
  required_checks:
    - ci/test-suite
    - ci/security-scan
    - ci/autonomous-safety-validation
  
  reviewers:
    - maintainer1
    - maintainer2
  
  labels:
    - ai-generated
    - enhancement
    - needs-review
```

### 3. Safety Validation Workflow

```yaml
# .github/workflows/autonomous-safety.yml
name: Autonomous Enhancement Safety
on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - '**.py'

jobs:
  safety-check:
    if: contains(github.event.pull_request.labels.*.name, 'ai-generated')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate autonomous changes
        run: |
          python scripts/validate_autonomous_changes.py
      - name: Security scan
        run: |
          bandit -r . -f json -o security-report.json
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            // Add safety validation results to PR
```

## Release Management

### 1. Semantic Versioning

Follow semantic versioning (semver) with these guidelines:

```yaml
Version Format: MAJOR.MINOR.PATCH

Examples:
  - 2.1.1: Current release
  - 2.1.2: Bug fixes and patches
  - 2.2.0: New features, backward compatible
  - 3.0.0: Breaking changes

Release Types:
  - alpha: Early development (2.2.0-alpha.1)
  - beta: Feature complete, testing (2.2.0-beta.1)
  - rc: Release candidate (2.2.0-rc.1)
  - stable: Production ready (2.2.0)
```

### 2. Release Process

#### Automated Release Workflow
```bash
# 1. Update version in VERSION file
echo "2.1.2" > VERSION

# 2. Update CHANGELOG.md with new release notes
# Add entry for new version

# 3. Commit changes
git add VERSION CHANGELOG.md
git commit -m "chore: prepare release v2.1.2"

# 4. Create and push tag
git tag -a v2.1.2 -m "Release v2.1.2"
git push origin main --tags

# 5. GitHub Actions automatically creates release
```

#### Manual Release Steps
1. **Prepare Release Branch**
   ```bash
   git checkout -b release/v2.1.2
   git push -u origin release/v2.1.2
   ```

2. **Update Version Files**
   - Update `VERSION` file
   - Update version in `README.md`
   - Update `CHANGELOG.md`

3. **Create Release PR**
   ```bash
   # Create PR from release branch to main
   gh pr create --title "Release v2.1.2" --body "Release preparation for v2.1.2"
   ```

4. **Tag and Release**
   ```bash
   # After PR is merged
   git checkout main
   git pull origin main
   git tag -a v2.1.2 -m "Release v2.1.2"
   git push origin v2.1.2
   ```

### 3. Release Assets

Automatic asset generation includes:

```yaml
Assets:
  - Source code (zip, tar.gz)
  - macOS application bundle (.app)
  - Windows executable (.exe)
  - Linux AppImage
  - Python wheel (.whl)
  - Documentation (PDF)
```

## Configuration Checklist

### Repository Setup
- [ ] Repository visibility set to public
- [ ] Description and topics configured
- [ ] Wiki and Discussions enabled
- [ ] Issues and Projects enabled
- [ ] Security features enabled

### Branch Protection
- [ ] Main branch protection configured
- [ ] Required status checks set up
- [ ] Review requirements configured
- [ ] Signed commits required

### GitHub Actions
- [ ] CI workflow tested and working
- [ ] Release workflow configured
- [ ] Dependency scanning enabled
- [ ] Security scanning active

### Community Features
- [ ] Issue templates tested
- [ ] PR template configured
- [ ] Discussion categories set up
- [ ] Project boards created

### Security Configuration
- [ ] SECURITY.md reviewed and updated
- [ ] Dependabot configured
- [ ] CodeQL scanning enabled
- [ ] Private vulnerability reporting enabled

### Autonomous Enhancement
- [ ] GitHub authentication configured
- [ ] Safety validation workflows active
- [ ] Autonomous configuration reviewed
- [ ] Required checks and reviewers set

### Release Management
- [ ] Semantic versioning strategy documented
- [ ] Automated release process tested
- [ ] Asset generation working
- [ ] CHANGELOG.md format established

## Troubleshooting

### Common Issues

#### Workflow Failures
```bash
# Check workflow status
gh workflow list
gh run list --workflow=ci.yml

# View workflow logs
gh run view [run-id]
```

#### Branch Protection Issues
```bash
# Verify protection rules
gh api repos/owner/repo/branches/main/protection

# Update protection rules
gh api repos/owner/repo/branches/main/protection \
  --method PUT \
  --input protection-config.json
```

#### Authentication Problems
```bash
# Test GitHub token
gh auth status

# Refresh authentication
gh auth refresh -s repo,workflow
```

### Support Resources

- **GitHub Docs**: https://docs.github.com
- **Actions Marketplace**: https://github.com/marketplace?type=actions
- **Community Forum**: https://github.community
- **SuperMini Issues**: https://github.com/rohnspringfield/supermini/issues

---

**Last Updated:** July 28, 2025
**Version:** 2.1.1

This guide should be updated as the repository configuration evolves and new features are added to the SuperMini project.