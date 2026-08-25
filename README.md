# CS Trivia

A lightweight site for computer science crosswords.

https://cstrivia.com

<img src="crossword/docs/img/readme.png" width="1300" />

## Design Approach

The backend delivers all necessary puzzle data in the initial HTTP response:

- The Django server sends the complete puzzle state upfront, including the solution  
- Solving logic (input handling, validation, and navigation) runs entirely in the client  
- No additional HTTP requests are made during solving (zero round-trips after load)  
- User progress is stored locally via session storage  

This design keeps the backend simple and makes solving feel more responsive by eliminating network round-trips, at the cost of server-side validation and persistence.

## Tech Stack
- Backend: Python, Django
- Database: PostgreSQL
- Frontend: **vanilla TypeScript** (no frontend framework)

## Architecture

A focus of this project is keeping a clear separation between backend data modeling and frontend state interaction.

- Uses Django’s ORM to model and query puzzle data
- Serializes data into simple DTO-like structures for the frontend
- Frontend manages puzzle state, user input, and board rendering without relying on a framework
- Backend handles data integrity and persistence, while the frontend focuses on interaction and rendering

### Why Django?

I chose Django for its ORM, built-in migrations, and server-side rendering, which make it easy to model data and iterate quickly.

Since the project is relatively small, keeping everything in a single repo felt simpler than splitting frontend and backend. Server-side rendering also makes it easy to pass data to the frontend without introducing a separate API layer.

This lets me focus on the core parts of the project: backend validation/modeling and frontend interaction.

I avoided using a frontend framework because the project didn’t require one, and I wanted to focus on core state management and DOM updates.

## Setup

```bash
git clone https://github.com/JuliusBoateng/cstrivia.git
cd cstrivia

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
````

> Use `python3` instead of `python` if your system does not map `python` to Python 3.

---

## Database Setup (PostgreSQL)

Install and start PostgreSQL:

```bash
brew install postgresql
brew services start postgresql
```

> These commands assume macOS with Homebrew installed.

Enter the Postgres shell (your local setup may vary):

```bash
psql postgres
```

Create the database:

```sql
CREATE DATABASE cstrivia;
\l  -- verify it exists
\q  -- exit shell
```

---

## Environment Setup

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

### Database URL

For most local setups:

```env
DATABASE_URL=postgres://localhost:5432/cstrivia
```

If you configured a user/password:

```env
DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/cstrivia
```

---

## Run Migrations

```bash
python manage.py migrate
```

Load puzzle data into postgres:

```bash
python manage.py load_puzzle crossword/fixtures/puzzles/open_source_basics.json
```

---

## Run Server

```bash
python manage.py runserver
```

The server should run without errors.

---

## Run Frontend

This project uses **vanilla TypeScript** compiled with **esbuild** for bundling and minification (no frontend framework).

Build frontend assets:

```bash
npm install
npm run build
```

For development (auto-rebuild on changes):

```bash
npm run watch
```

Visit: [http://localhost:8000/](http://localhost:8000/)
> Make sure you're using **http**, not https.
> Some browsers (like Chrome) may auto-redirect to https, which will cause errors.

---

## Django Admin (Optional)

The admin panel allows you to update puzzles and design notes without directly updating the database. 

Create a superuser to access the Django admin interface:

```bash
python manage.py createsuperuser
```
Follow the prompts to set a username and password.

Visit the admin interface:

http://localhost:8000/admin

From the admin panel, you can create and manage puzzles and design notes.

---

## Feedback

Feedback or suggestions? Open an issue or email julius@cstrivia.com

---

## Licensing

Source code is licensed under the MIT License. See LICENSE for details.

Puzzle content (including puzzle grids, clues, answers, puzzle metadata, and
design notes) is licensed under CC BY 4.0. See LICENSE-CONTENT for details.

Externally hosted images, illustrations, videos, and other media are not
covered by these licenses unless otherwise stated.