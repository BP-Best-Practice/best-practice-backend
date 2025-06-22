commit_history = [
    {
        "commit": "a1b2c3d4e5f6g78h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z",
        "author": "Jane Doe",
        "date": "2023-10-01",
        "message": "Initial commit with basic structure",
        "files_changed": 5,
        "lines_added": 150,
        "lines_deleted": 10,
        "branches": ["main", "develop"],
        "tags": ["v1.0", "stable"],
    },
    {
        "commit": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z67",
        "author": "Jane Doe",
        "date": "2023-10-02",
        "message": "Added new feature for user authentication",
        "files_changed": 10,
        "lines_added": 300,
        "lines_deleted": 20,
        "branches": ["main", "feature/auth"],
        "tags": ["v1.1", "feature"],
    },
    {
        "commit": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z678",
        "author": "Jane Doe",
        "date": "2023-10-03",
        "message": "Fixed bug in user profile page",
        "files_changed": 3,
        "lines_added": 50,
        "lines_deleted": 5,
        "branches": ["main", "bugfix/profile"],
        "tags": ["v1.2", "bugfix"],
    },
    {
        "commit": "d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z67890",
        "author": "Jane Doe",
        "date": "2023-10-04",
        "message": "Updated documentation for API endpoints",
        "files_changed": 2,
        "lines_added": 100,
        "lines_deleted": 0,
        "branches": ["main", "docs"],
        "tags": ["v1.3", "documentation"],
    },
]


test_pr_generation = {
    "title": "Test PR",
    "description": "This is a test PR",
    "base_branch": "main",
    "target_branch": "feature/test-pr",
}