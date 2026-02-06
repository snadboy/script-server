# GitHub Repository Browser for Import Dialog

## Overview

Enhance the Import Project dialog to allow Git Clone via:
1. **Direct URL** (current) - Paste any Git URL
2. **Browse GitHub** (new) - Search repositories for a GitHub user

Similar to how ZIP Upload has a file picker and Local Path has a directory browser.

---

## UI/UX Design

### Current State (Git Clone)
```
┌─────────────────────────────────────┐
│ Repository URL                      │
│ ┌─────────────────────────────────┐ │
│ │ https://github.com/user/repo    │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Branch (optional)                   │
│ ┌─────────────────────────────────┐ │
│ │ main                            │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Proposed Design (Git Clone with Browser)
```
┌─────────────────────────────────────────────────────────┐
│ Import Source                                           │
│ ○ Direct URL    ● Browse GitHub                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ GitHub Username                                         │
│ ┌────────────────────────┬──────────┐                   │
│ │ snadboy               │ [Search] │                   │
│ └────────────────────────┴──────────┘                   │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🔍 Filter: [____________]                           │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ ✓ gmail-trim ⭐ 5                                   │ │
│ │   Email cleanup automation for Gmail               │ │
│ │   Updated: 2 days ago                              │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │   script-server (fork)                             │ │
│ │   Web UI for running Python scripts               │ │
│ │   Updated: 1 week ago                              │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │   upcoming-episodes                                │ │
│ │   TV show episode tracker                          │ │
│ │   Updated: 3 weeks ago                             │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Branch: [main ▼]                                        │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Backend API

**New Endpoint:** `GET /admin/github/repos?username=<user>`

**File:** `src/web/server.py`

```python
class GitHubReposHandler(BaseRequestHandler):
    """Handler for fetching GitHub user repositories."""

    @inject_user
    @requires_admin
    def get(self):
        username = self.get_argument('username', None)
        if not username:
            self.send_error(400, reason='Username required')
            return

        # Fetch repos from GitHub API
        repos = self._fetch_github_repos(username)
        self.write(json.dumps({'repositories': repos}))

    def _fetch_github_repos(self, username: str) -> list:
        """Fetch public repositories for a GitHub user."""
        import requests

        url = f'https://api.github.com/users/{username}/repos'
        params = {
            'sort': 'updated',
            'per_page': 100,
            'type': 'all'  # owner, public, private (requires auth)
        }

        headers = {'Accept': 'application/vnd.github.v3+json'}

        # Optional: Add GitHub token for higher rate limits
        # github_token = os.getenv('GITHUB_TOKEN')
        # if github_token:
        #     headers['Authorization'] = f'token {github_token}'

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            repos_data = response.json()

            # Transform to simplified format
            return [
                {
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo['description'],
                    'clone_url': repo['clone_url'],
                    'html_url': repo['html_url'],
                    'stars': repo['stargazers_count'],
                    'language': repo['language'],
                    'updated_at': repo['updated_at'],
                    'is_fork': repo['fork'],
                    'default_branch': repo['default_branch']
                }
                for repo in repos_data
            ]
        except requests.RequestException as e:
            raise ValueError(f'Failed to fetch GitHub repositories: {str(e)}')
```

**Register route:**
```python
(r'/admin/github/repos', GitHubReposHandler)
```

---

### Phase 2: Frontend Component

**File:** `web-src/src/main-app/components/ImportProjectModal.vue`

#### 2.1 Add Data Properties

```javascript
data() {
  return {
    // ... existing properties ...

    // GitHub browser
    gitInputMode: 'url',  // 'url' or 'browse'
    githubUsername: '',
    githubRepos: [],
    loadingRepos: false,
    repoFilter: '',
    selectedRepo: null,
  };
}
```

#### 2.2 Add Computed Properties

```javascript
computed: {
  filteredRepos() {
    if (!this.repoFilter) return this.githubRepos;

    const filter = this.repoFilter.toLowerCase();
    return this.githubRepos.filter(repo =>
      repo.name.toLowerCase().includes(filter) ||
      (repo.description && repo.description.toLowerCase().includes(filter))
    );
  },

  canImportGit() {
    if (this.gitInputMode === 'url') {
      return !!this.gitUrl;
    } else {
      return !!this.selectedRepo;
    }
  }
}
```

#### 2.3 Add Methods

```javascript
methods: {
  async fetchGitHubRepos() {
    if (!this.githubUsername) return;

    this.loadingRepos = true;
    this.error = null;

    try {
      const response = await axiosInstance.get('/admin/github/repos', {
        params: { username: this.githubUsername }
      });

      this.githubRepos = response.data.repositories || [];

      if (this.githubRepos.length === 0) {
        this.error = `No repositories found for user "${this.githubUsername}"`;
      }
    } catch (e) {
      this.error = e.response?.data?.message || 'Failed to fetch GitHub repositories';
      this.githubRepos = [];
    } finally {
      this.loadingRepos = false;
    }
  },

  selectRepo(repo) {
    this.selectedRepo = repo;
    this.gitUrl = repo.clone_url;
    this.gitBranch = repo.default_branch;
  },

  switchToUrlMode() {
    this.gitInputMode = 'url';
    this.selectedRepo = null;
  },

  switchToBrowseMode() {
    this.gitInputMode = 'browse';
  }
}
```

#### 2.4 Update Template (Git Import Section)

```vue
<div v-if="importType === 'git'" class="import-form">
  <!-- Input Mode Toggle -->
  <div class="input-mode-toggle">
    <button
      :class="['mode-btn', { active: gitInputMode === 'url' }]"
      @click="switchToUrlMode"
    >
      Direct URL
    </button>
    <button
      :class="['mode-btn', { active: gitInputMode === 'browse' }]"
      @click="switchToBrowseMode"
    >
      Browse GitHub
    </button>
  </div>

  <!-- Direct URL Mode -->
  <div v-if="gitInputMode === 'url'">
    <div class="form-group">
      <label>Repository URL</label>
      <input
        v-model="gitUrl"
        type="text"
        placeholder="https://github.com/user/repo"
        class="form-input"
        :disabled="importing"
      />
    </div>
    <div class="form-group">
      <label>Branch (optional)</label>
      <input
        v-model="gitBranch"
        type="text"
        placeholder="main"
        class="form-input"
        :disabled="importing"
      />
    </div>
  </div>

  <!-- Browse GitHub Mode -->
  <div v-else-if="gitInputMode === 'browse'">
    <!-- Username Input -->
    <div class="form-group">
      <label>GitHub Username</label>
      <div class="search-row">
        <input
          v-model="githubUsername"
          type="text"
          placeholder="username"
          class="form-input"
          :disabled="loadingRepos"
          @keyup.enter="fetchGitHubRepos"
        />
        <button
          class="btn-search"
          :disabled="!githubUsername || loadingRepos"
          @click="fetchGitHubRepos"
        >
          {{ loadingRepos ? 'Loading...' : 'Search' }}
        </button>
      </div>
    </div>

    <!-- Repository List -->
    <div v-if="githubRepos.length > 0" class="repo-list-container">
      <!-- Filter Input -->
      <div class="filter-input">
        <i class="material-icons">search</i>
        <input
          v-model="repoFilter"
          type="text"
          placeholder="Filter repositories..."
          class="form-input-inline"
        />
      </div>

      <!-- Repository Items -->
      <div class="repo-list">
        <div
          v-for="repo in filteredRepos"
          :key="repo.full_name"
          :class="['repo-item', { selected: selectedRepo?.full_name === repo.full_name }]"
          @click="selectRepo(repo)"
        >
          <div class="repo-header">
            <span class="repo-name">{{ repo.name }}</span>
            <div class="repo-badges">
              <span v-if="repo.is_fork" class="badge-fork">fork</span>
              <span v-if="repo.stars > 0" class="badge-stars">
                ⭐ {{ repo.stars }}
              </span>
            </div>
          </div>
          <p v-if="repo.description" class="repo-description">
            {{ repo.description }}
          </p>
          <div class="repo-meta">
            <span v-if="repo.language" class="repo-language">{{ repo.language }}</span>
            <span class="repo-updated">Updated {{ formatRelativeTime(repo.updated_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Repository Display -->
    <div v-if="selectedRepo" class="selected-repo">
      <div class="selected-label">Selected:</div>
      <div class="selected-name">{{ selectedRepo.full_name }}</div>
      <div class="form-group">
        <label>Branch</label>
        <input
          v-model="gitBranch"
          type="text"
          :placeholder="selectedRepo.default_branch"
          class="form-input"
        />
      </div>
    </div>
  </div>
</div>
```

---

### Phase 3: Styling

```css
/* Input Mode Toggle */
.input-mode-toggle {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border: 1px solid #333333;
  border-radius: 6px;
  padding: 4px;
  background: #1a1a1a;
}

.mode-btn {
  flex: 1;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: #999999;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.mode-btn:hover {
  background: #2a2a2a;
  color: #e0e0e0;
}

.mode-btn.active {
  background: #5dade2;
  color: #000;
  font-weight: 500;
}

/* Search Row */
.search-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-row .form-input {
  flex: 1;
}

.btn-search {
  padding: 10px 20px;
  background: #5dade2;
  color: #000;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-search:hover:not(:disabled) {
  background: #4a9fd6;
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Repository List */
.repo-list-container {
  border: 1px solid #333333;
  border-radius: 6px;
  overflow: hidden;
  margin-top: 12px;
}

.filter-input {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #1a1a1a;
  border-bottom: 1px solid #333333;
}

.filter-input i {
  color: #999999;
  font-size: 20px;
}

.form-input-inline {
  flex: 1;
  background: transparent;
  border: none;
  color: #e0e0e0;
  font-size: 14px;
  outline: none;
}

.repo-list {
  max-height: 300px;
  overflow-y: auto;
  background: #222222;
}

.repo-item {
  padding: 12px;
  border-bottom: 1px solid #333333;
  cursor: pointer;
  transition: all 0.2s;
}

.repo-item:hover {
  background: #2a2a2a;
}

.repo-item.selected {
  background: rgba(93, 173, 226, 0.15);
  border-left: 3px solid #5dade2;
}

.repo-item:last-child {
  border-bottom: none;
}

.repo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.repo-name {
  font-weight: 600;
  color: #e0e0e0;
  font-size: 14px;
}

.repo-badges {
  display: flex;
  gap: 6px;
}

.badge-fork,
.badge-stars {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  background: #333333;
  color: #999999;
}

.badge-stars {
  background: rgba(255, 215, 0, 0.15);
  color: #ffd700;
}

.repo-description {
  font-size: 13px;
  color: #999999;
  margin: 4px 0;
  line-height: 1.4;
}

.repo-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666666;
  margin-top: 6px;
}

.repo-language {
  font-weight: 500;
}

/* Selected Repository */
.selected-repo {
  margin-top: 16px;
  padding: 12px;
  background: rgba(93, 173, 226, 0.1);
  border: 1px solid rgba(93, 173, 226, 0.3);
  border-radius: 6px;
}

.selected-label {
  font-size: 11px;
  color: #999999;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.selected-name {
  font-size: 14px;
  font-weight: 600;
  color: #5dade2;
  margin-bottom: 12px;
}
```

---

## Features

### Implemented
✅ Toggle between Direct URL and Browse GitHub
✅ Fetch public repositories for any GitHub user
✅ Searchable/filterable repository list
✅ Sort by most recently updated
✅ Show stars, language, fork status
✅ Auto-populate URL and branch on selection
✅ Visual indication of selected repository

### Optional Enhancements
- 🔄 GitHub authentication for private repos
- 🔄 Pagination for users with 100+ repos
- 🔄 Remember last-used GitHub username
- 🔄 Show repo size and license
- 🔄 Sort by stars/name/updated date
- 🔄 Organization repository browsing

---

## Benefits

**User Experience:**
- ✅ No need to remember full GitHub URLs
- ✅ Browse your own repos quickly
- ✅ Discover repositories visually
- ✅ See repo metadata before importing
- ✅ Consistent with ZIP/Local file browsing pattern

**Developer Experience:**
- ✅ Reusable GitHub API integration
- ✅ Clean separation: Direct URL vs Browse
- ✅ Rate limit handling (100 req/hour unauthenticated)
- ✅ Optional GitHub token for higher limits

---

## Rate Limiting

GitHub API limits (unauthenticated):
- **60 requests per hour** per IP
- **5000 requests per hour** with authentication token

**Mitigation:**
- Cache repository lists in localStorage
- Optional GitHub token configuration in settings
- Show rate limit remaining in UI

---

## Next Steps

1. ✅ Review and approve plan
2. Implement backend endpoint
3. Implement frontend UI
4. Test with various GitHub users
5. Add optional GitHub token configuration
6. Update documentation

---

**Status:** 📋 Plan ready for review and implementation
