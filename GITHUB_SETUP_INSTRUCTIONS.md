# GitHub Repository Setup Instructions

This document provides step-by-step instructions to create the GitHub repository for SuperMini and configure it properly.

## Step 1: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)
```bash
# Install GitHub CLI if not already installed
# macOS: brew install gh
# Linux: Follow https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# Login to GitHub
gh auth login

# Create repository
gh repo create supermini --public --description "SuperMini - Desktop AI Assistant with Claude API and Ollama integration. Features autonomous enhancement, multimedia processing, and intelligent task automation." --homepage "https://github.com/your-username/supermini"

# Set upstream and push
git remote add origin https://github.com/your-username/supermini.git
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Web Interface
1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `supermini`
   - **Description**: `SuperMini - Desktop AI Assistant with Claude API and Ollama integration. Features autonomous enhancement, multimedia processing, and intelligent task automation.`
   - **Visibility**: Public
   - **Initialize**: Do NOT initialize with README, .gitignore, or license (we already have these)

3. Click "Create repository"

4. Connect local repository to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/supermini.git
git branch -M main
git push -u origin main
```

## Step 2: Configure Repository Settings

After creating the repository, configure these settings in GitHub:

### Repository Settings
1. Go to repository → Settings → General
2. **Features**:
   - ✅ Issues
   - ✅ Projects  
   - ✅ Wiki
   - ✅ Discussions
   - ✅ Sponsorships (optional)

3. **Pull Requests**:
   - ✅ Allow merge commits
   - ✅ Allow squash merging
   - ✅ Allow rebase merging
   - ✅ Always suggest updating pull request branches
   - ✅ Allow auto-merge
   - ✅ Automatically delete head branches

### Branch Protection Rules
1. Go to Settings → Branches
2. Add rule for `main` branch:
   - **Branch name pattern**: `main`
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require conversation resolution before merging
   - ✅ Include administrators

### Security Settings
1. Go to Settings → Security & analysis
2. **Dependency graph**: ✅ Enable
3. **Dependabot alerts**: ✅ Enable
4. **Dependabot security updates**: ✅ Enable
5. **Code scanning alerts**: ✅ Enable
6. **Secret scanning alerts**: ✅ Enable

### Actions Permissions
1. Go to Settings → Actions → General
2. **Actions permissions**: Allow all actions and reusable workflows
3. **Artifact and log retention**: 90 days (default)
4. **Fork pull request workflows**: Require approval for all outside collaborators

## Step 3: Set Up Repository Secrets (For Release Automation)

For automated releases to work, you'll need to set up these secrets:

1. Go to Settings → Secrets and variables → Actions
2. Add the following repository secrets:

### Required Secrets
- **GITHUB_TOKEN**: Automatically provided by GitHub (no action needed)

### Optional Secrets (for enhanced functionality)
- **ANTHROPIC_API_KEY**: Your Claude API key (for testing)
- **CODECOV_TOKEN**: For code coverage reporting (get from https://codecov.io)

## Step 4: Configure GitHub Pages (Optional)

To host documentation:

1. Go to Settings → Pages
2. **Source**: Deploy from a branch
3. **Branch**: main
4. **Folder**: /docs
5. Save

## Step 5: Create Initial Release

After pushing to GitHub:

```bash
# Create and push initial tag
git tag -a v2.0.0 -m "Initial open-source release"
git push origin v2.0.0
```

This will trigger the release workflow and create the first GitHub release.

## Step 6: Community Health Files

The repository already includes:
- ✅ README.md
- ✅ LICENSE  
- ✅ CONTRIBUTING.md
- ✅ Issue templates
- ✅ Pull request template
- ✅ Security policy (in .github/SECURITY.md if created)

## Step 7: Repository Topics

Add these topics to help discoverability:

1. Go to repository main page
2. Click the gear icon next to "About"
3. Add topics:
   - `ai`
   - `desktop-app`
   - `claude-api`
   - `ollama`
   - `pyqt6`
   - `automation`
   - `autonomous-ai`
   - `multimedia-processing`
   - `python`
   - `macos`
   - `linux`
   - `windows`

## Step 8: Enable Discussions (Optional)

1. Go to Settings → General
2. Scroll to Features
3. ✅ Enable Discussions

Create initial discussion categories:
- General
- Q&A
- Feature Requests
- Show and Tell

## Verification Checklist

After setup, verify:
- [ ] Repository is public and accessible
- [ ] All files pushed successfully
- [ ] GitHub Actions are enabled and workflows appear
- [ ] Issue templates work correctly
- [ ] Branch protection rules are active
- [ ] Security features are enabled
- [ ] Topics are added
- [ ] Repository description is set

## Post-Setup Commands

```bash
# Verify remote connection
git remote -v

# Check if Actions are working
git log --oneline -5

# Test issue creation (optional)
gh issue create --title "Test Issue" --body "Testing GitHub integration"

# View repository info
gh repo view
```

## Troubleshooting

### Common Issues

1. **Push fails with authentication error**:
   ```bash
   gh auth refresh
   # or
   git remote set-url origin https://github.com/USERNAME/supermini.git
   ```

2. **GitHub Actions not running**:
   - Check Actions permissions in repository settings
   - Verify workflow files are in `.github/workflows/`
   - Check for YAML syntax errors

3. **Branch protection preventing pushes**:
   - Temporarily disable protection for initial setup
   - Use pull requests for future changes

4. **Release automation not working**:
   - Verify `VERSION` file exists
   - Check that semantic-version package is installed
   - Ensure GitHub token has proper permissions

## Next Steps

After successful setup:
1. Update README.md with correct GitHub URLs
2. Test the CI/CD pipeline with a small change
3. Create your first enhancement using 'Enhance Yourself' mode
4. Verify that automatic releases work correctly
5. Invite collaborators (if desired)
6. Set up project boards for issue tracking

Your SuperMini repository is now ready for open-source collaboration!