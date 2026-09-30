# Thiết kế Resource cho Blog API (Lab 1)

## 1. Xác định Resources
- `users`: Người dùng / tác giả
- `posts`: Bài viết
- `comments`: Bình luận
- `tags`: Thẻ bài viết
- `profile`: Hồ sơ người dùng
- `followers` / `following`: Quan hệ theo dõi

---

## 2. Phân loại Resource
- **Collection**: `/posts`, `/users`, `/tags`
- **Item**: `/posts/{id}`, `/users/{id}`, `/tags/{id}`
- **Sub-resource**:
  - `/posts/{id}/comments` (Collection) & `/posts/{id}/comments/{id}` (Item)
  - `/posts/{id}/tags` & `/posts/{id}/tags/{id}`
  - `/users/{id}/posts`
  - `/users/{id}/followers` & `/users/{id}/following/{target_id}`
- **Singleton**: `/users/{id}/profile`

---

## 3. Sơ đồ cây Endpoint (Prefix: `/api/v1`)

```text
/api/v1
├── /posts
│   └── /{id}
│       ├── /comments
│       │   └── /{id}
│       └── /tags
│           └── /{id}
├── /users
│   └── /{id}
│       ├── /profile
│       ├── /posts
│       ├── /followers
│       └── /following
│           └── /{target_id}
└── /tags
    └── /{id}
        └── /posts
```

### Danh sách API chính cho `/posts`:
- `GET /api/v1/posts` — Lấy danh sách bài viết
- `POST /api/v1/posts` — Tạo bài viết mới
- `GET /api/v1/posts/<id>` — Chi tiết bài viết
- `PUT /api/v1/posts/<id>` — Cập nhật bài viết
- `DELETE /api/v1/posts/<id>` — Xóa bài viết
