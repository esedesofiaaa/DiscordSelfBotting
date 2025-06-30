#!/bin/bash
# Branch management helper script for Discord Bot project

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_help() {
    echo -e "${BLUE}Discord Bot Branch Management${NC}"
    echo ""
    echo "Usage: ./branch-helper.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  init              Initialize development workflow"
    echo "  feature <name>    Create and switch to new feature branch"
    echo "  finish <name>     Merge feature branch to develop"
    echo "  release           Create release from develop to main"
    echo "  hotfix <name>     Create hotfix branch from main"
    echo "  status            Show current branch status"
    echo ""
    echo "Examples:"
    echo "  ./branch-helper.sh init"
    echo "  ./branch-helper.sh feature add-new-command"
    echo "  ./branch-helper.sh finish add-new-command"
    echo "  ./branch-helper.sh release"
    echo "  ./branch-helper.sh hotfix fix-crash-bug"
}

init_workflow() {
    echo -e "${BLUE}🔧 Initializing development workflow...${NC}"
    
    # Create develop branch if it doesn't exist
    if ! git show-ref --verify --quiet refs/heads/develop; then
        echo -e "${GREEN}Creating develop branch...${NC}"
        git checkout -b develop
        git push -u origin develop
    else
        echo -e "${YELLOW}develop branch already exists${NC}"
    fi
    
    # Switch to develop
    git checkout develop
    git pull origin develop
    
    echo -e "${GREEN}✅ Development workflow initialized${NC}"
    echo -e "${BLUE}You are now on the develop branch${NC}"
}

create_feature() {
    local feature_name="$1"
    if [ -z "$feature_name" ]; then
        echo -e "${RED}❌ Please provide a feature name${NC}"
        echo "Usage: ./branch-helper.sh feature <name>"
        exit 1
    fi
    
    # Ensure we're on latest develop
    git checkout develop
    git pull origin develop
    
    # Create and switch to feature branch
    local branch_name="feature/$feature_name"
    echo -e "${GREEN}Creating feature branch: $branch_name${NC}"
    
    git checkout -b "$branch_name"
    git push -u origin "$branch_name"
    
    echo -e "${GREEN}✅ Feature branch created and pushed${NC}"
    echo -e "${BLUE}You are now on: $branch_name${NC}"
    echo ""
    echo -e "${YELLOW}💡 Development tips:${NC}"
    echo "  • Make your changes and commits"
    echo "  • Push regularly: git push"
    echo "  • When ready: ./branch-helper.sh finish $feature_name"
}

finish_feature() {
    local feature_name="$1"
    if [ -z "$feature_name" ]; then
        echo -e "${RED}❌ Please provide the feature name to finish${NC}"
        echo "Usage: ./branch-helper.sh finish <name>"
        exit 1
    fi
    
    local branch_name="feature/$feature_name"
    
    # Check if we're on the feature branch
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "$branch_name" ]; then
        echo -e "${YELLOW}Switching to feature branch: $branch_name${NC}"
        git checkout "$branch_name"
    fi
    
    # Push any pending changes
    git push
    
    # Switch to develop and merge
    git checkout develop
    git pull origin develop
    git merge "$branch_name" --no-ff -m "Merge feature: $feature_name"
    git push origin develop
    
    # Clean up
    echo -e "${YELLOW}Cleaning up feature branch...${NC}"
    git branch -d "$branch_name"
    git push origin --delete "$branch_name"
    
    echo -e "${GREEN}✅ Feature merged into develop${NC}"
    echo -e "${BLUE}Feature branch cleaned up${NC}"
}

create_release() {
    echo -e "${BLUE}🚀 Creating release from develop to main...${NC}"
    
    # Ensure develop is up to date
    git checkout develop
    git pull origin develop
    
    # Merge develop into main
    git checkout main
    git pull origin main
    git merge develop --no-ff -m "Release: Merge develop into main"
    
    echo -e "${GREEN}✅ Release created${NC}"
    echo -e "${YELLOW}⚠️  About to push to main - this will trigger deployment!${NC}"
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        echo -e "${GREEN}🚀 Deployment triggered!${NC}"
        echo -e "${BLUE}Check GitHub Actions for deployment status${NC}"
    else
        echo -e "${YELLOW}Release created locally but not pushed${NC}"
        echo -e "${BLUE}Run 'git push origin main' when ready to deploy${NC}"
    fi
}

create_hotfix() {
    local hotfix_name="$1"
    if [ -z "$hotfix_name" ]; then
        echo -e "${RED}❌ Please provide a hotfix name${NC}"
        echo "Usage: ./branch-helper.sh hotfix <name>"
        exit 1
    fi
    
    # Create hotfix from main
    git checkout main
    git pull origin main
    
    local branch_name="hotfix/$hotfix_name"
    git checkout -b "$branch_name"
    git push -u origin "$branch_name"
    
    echo -e "${GREEN}✅ Hotfix branch created: $branch_name${NC}"
    echo -e "${YELLOW}💡 When ready, merge back to both main and develop${NC}"
}

show_status() {
    echo -e "${BLUE}📊 Current Branch Status${NC}"
    echo ""
    
    local current_branch=$(git branch --show-current)
    echo -e "${GREEN}Current branch: $current_branch${NC}"
    echo ""
    
    # Show recent commits
    echo -e "${BLUE}Recent commits:${NC}"
    git log --oneline -5
    echo ""
    
    # Show branch comparison
    if [ "$current_branch" != "main" ]; then
        echo -e "${BLUE}Commits ahead of main:${NC}"
        git log main..HEAD --oneline || echo "No commits ahead"
        echo ""
    fi
    
    # Show status
    echo -e "${BLUE}Working directory status:${NC}"
    git status --short
}

# Main script logic
case "${1:-}" in
    "init")
        init_workflow
        ;;
    "feature")
        create_feature "$2"
        ;;
    "finish")
        finish_feature "$2"
        ;;
    "release")
        create_release
        ;;
    "hotfix")
        create_hotfix "$2"
        ;;
    "status")
        show_status
        ;;
    "help"|"--help"|"-h"|"")
        print_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_help
        exit 1
        ;;
esac
