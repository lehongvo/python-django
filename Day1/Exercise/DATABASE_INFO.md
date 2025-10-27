# 📊 Database Information - Django Blog

## Loại Database: SQLite

File database: `db.sqlite3` (132KB)

### SQLite là gì?

**SQLite** là một database rất nhẹ, nhúng vào trong ứng dụng.

**Đặc điểm:**
- ✅ Không cần cài đặt server riêng
- ✅ Tất cả dữ liệu trong **1 file duy nhất** (`db.sqlite3`)
- ✅ Phù hợp cho development và ứng dụng nhỏ
- ✅ Không cần cấu hình
- ✅ Nhanh cho dữ liệu nhỏ
- ❌ Không phù hợp cho production lớn (nên dùng PostgreSQL/MySQL)

### Cấu trúc Database

Dựa vào file cấu hình `blogproject/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # File SQLite
    }
}
```

### Các Tables trong Database

Database này chứa các bảng sau:

#### 1. `blog_blogpost` (Table chính của ứng dụng)

**Cấu trúc:**
```sql
CREATE TABLE blog_blogpost (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    published_date DATETIME NOT NULL,
    is_published BOOLEAN NOT NULL DEFAULT 0
);
```

**Các trường:**
- `id`: ID tự động (Primary Key)
- `title`: Tiêu đề bài viết (max 200 ký tự)
- `content`: Nội dung bài viết (không giới hạn)
- `author`: Tác giả (max 100 ký tự)
- `published_date`: Ngày đăng (tự động)
- `is_published`: Đã xuất bản? (True/False)

#### 2. Các bảng mặc định của Django

- `django_migrations`: Lưu trạng thái migrations
- `django_content_type`: Quản lý content types
- `django_session`: Quản lý sessions
- `auth_user`: Người dùng và admin
- `auth_group`: Nhóm người dùng
- `auth_permission`: Quyền truy cập
- `auth_user_groups`: Liên kết user và group
- `auth_user_user_permissions`: Quyền của user

### Xem Database

#### Cách 1: Qua Django Shell

```bash
# Trong container Docker
docker-compose exec web python manage.py shell

# Trong shell, xem tất cả posts:
>>> from blog.models import BlogPost
>>> BlogPost.objects.all()
>>> BlogPost.objects.count()
```

#### Cách 2: Qua Admin Panel

1. Truy cập: http://localhost:8000/admin
2. Login với admin/admin123
3. Click vào "Blog posts"
4. Xem tất cả dữ liệu

#### Cách 3: Qua SQLite Command Line

```bash
# Liệt kê tables
sqlite3 db.sqlite3 ".tables"

# Xem cấu trúc bảng
sqlite3 db.sqlite3 ".schema blog_blogpost"

# Xem dữ liệu
sqlite3 db.sqlite3 "SELECT * FROM blog_blogpost;"

# Đếm số posts
sqlite3 db.sqlite3 "SELECT COUNT(*) FROM blog_blogpost;"
```

### Thao tác với Database qua Django

#### Thêm dữ liệu mẫu:

```python
from blog.models import BlogPost

post = BlogPost.objects.create(
    title="Tiêu đề bài viết",
    content="Nội dung bài viết",
    author="Tên tác giả",
    is_published=True
)
```

#### Xem dữ liệu:

```python
# Tất cả posts
posts = BlogPost.objects.all()

# Posts đã publish
posts = BlogPost.objects.filter(is_published=True)

# 1 post cụ thể
post = BlogPost.objects.get(id=1)
```

#### Sửa dữ liệu:

```python
post = BlogPost.objects.get(id=1)
post.title = "Tiêu đề mới"
post.save()
```

#### Xóa dữ liệu:

```python
post = BlogPost.objects.get(id=1)
post.delete()
```

### Migration (Di chuyển database)

Django dùng migrations để thay đổi cấu trúc database:

```bash
# Tạo migration files khi thay đổi models
python manage.py makemigrations

# Áp dụng migrations vào database
python manage.py migrate

# Xem trạng thái migrations
python manage.py showmigrations

# Xem SQL của migration
python manage.py sqlmigrate blog 0001
```

### Backup Database

SQLite database chỉ là 1 file, backup rất đơn giản:

```bash
# Copy file
cp db.sqlite3 db.sqlite3.backup

# Hoặc compress
tar -czf backup.tar.gz db.sqlite3
```

### Kích thước Database

Hiện tại: **132KB** (rất nhỏ!)

Bao gồm:
- 2 sample blog posts
- Admin user data
- Django system tables

### Upgrade lên PostgreSQL (Production)

Khi cần scalability cao hơn, có thể chuyển sang PostgreSQL:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Location của Database

File location: `/Day1/Exercise/db.sqlite3`

Được tạo tự động khi chạy lần đầu `python manage.py migrate`

### File không nên commit lên Git

File `db.sqlite3` đã được thêm vào `.gitignore` vì:
- Chứa dữ liệu development
- Không cần thiết trong repository
- Mỗi developer sẽ có database riêng
- Có thể tái tạo bằng migrations

### Tóm tắt

| Feature | SQLite | PostgreSQL (Production) |
|---------|--------|-------------------------|
| File size | 132KB | N/A |
| Cài đặt | Đã có sẵn | Cần cài riêng |
| Server | Không cần | Cần |
| Phù hợp cho | Dev, Testing | Production |
| Performance | Tốt (nhỏ) | Xuất sắc (lớn) |
| Concurrent users | Ít | Nhiều |
| Backup | Copy 1 file | pg_dump |

---

**Current Status**: ✅ Database đã có 2 sample posts và sẵn sàng sử dụng!

