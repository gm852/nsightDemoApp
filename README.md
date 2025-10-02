# User Profile Card - Frontend & Backend


## Project Structure

```
nsightTechnicalAssessment/
├── frontend/                 # Next.js react app stuff
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx     # main page with UserProfileCard
│   │   └── components/
│   │       └── UserProfileCard.tsx  # user profile component
│   └── package.json
├── backend/                  # FastAPI Python app
│   ├── app.py               # Main app 
│   ├── database.py          # SQLalc models and database stuff
│   ├── models.py            # Response models
│   ├── services.py          # Logic and caching
│   ├── config.py            # config
│   ├── requirements.txt     # Dependencies
│   ├── alembic/             # Database migrations
│   │   ├── versions/
│   │   │   └── 001_create_users_table.py
│   │   ├── env.py
│   │   └── script.py.mako
│   └── alembic.ini
└── README.md
```

## Setup

### Pre reqs
- Node.js 18+ and npm or bun
- Python 3.8+ with pip
- PostgreSQL 12+ (or Docker for containerized setup)

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
Run PostgreSQL using Docker (use `sudo` if required):

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=root \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=nsightTechnicalTest \
  -p 5432:5432 \
  postgres:latest
```

5. Start the FastAPI server:
```bash
python app.py
```

The backend API will be available at `http://localhost:8000`

## Data Flow

1. **Frontend Request**: UserProfileCard component calls `http://localhost:8000/api/users/1`
2. **Backend Check**: Backend checks if data exists in PostgreSQL and if it's fresh (≤10 minutes old)
3. **Cache Hit**: If data is fresh, return from PostgreSQL
4. **Cache Miss**: If data is stale/missing, fetch from `https://jsonplaceholder.typicode.com/users/1`
5. **Normalize & Store**: Backend normalizes the data (flattens company object, adds https:// to website) and upserts into PostgreSQL
6. **Return**: Backend returns the normalized data to frontend
7. **Display**: Frontend displays the user profile with interactive "View Details" button

### Environment Variables

The application uses these environment variables (set automatically in Docker Compose):

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/nsightTechnicalTest
UPSTREAM_API_URL=https://jsonplaceholder.typicode.com/users/1
CACHE_DURATION_MINUTES=10
```

For manual setup, you can create a `.env` file in the backend directory with these values.

## API Usage Examples

### Basic API Calls

#### Get User Data (with caching)
```bash
curl http://localhost:8000/api/users/1
```

#### Force Refresh User Data
```bash
curl -X POST http://localhost:8000/api/users/refresh
```

#### Get User Data (bypass cache)
```bash
curl "http://localhost:8000/api/users/1?bypassCache=true"
```

#### Health Check
```bash
curl http://localhost:8000/health
```

### Advanced API Calls with Headers

#### Get User Data with JSON formatting
```bash
curl -H "Accept: application/json" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/users/1
```

#### Force Refresh with verbose output
```bash
curl -X POST \
     -H "Accept: application/json" \
     -H "Content-Type: application/json" \
     -v \
     http://localhost:8000/api/users/refresh
```

#### Test API with timeout and retry
```bash
curl --connect-timeout 10 \
     --max-time 30 \
     --retry 3 \
     http://localhost:8000/api/users/1
```

### API Documentation

#### Access Swagger UI
```bash
# Open in browser
open http://localhost:8000/docs

# Or get OpenAPI schema
curl http://localhost:8000/openapi.json
```

## Testing the Application

1. Start both frontend and backend servers
2. Open `http://localhost:3000` in your browser
3. The UserProfileCard should load and display user data
4. Click "View Details" to toggle company information
5. Test the backend API endpoints using the curl commands above


## Common Issues
If you encounter "Cross origin request detected from <IP>" then add your origin IP to `frontend/next.config.ts`