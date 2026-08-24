# ==============================================================================
# Stage 1: Builder stage using uv
# ==============================================================================
FROM python:3.14-slim AS builder

WORKDIR /app

# Copy official uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install production dependencies without dev dependencies
RUN uv sync --frozen --no-dev --no-install-project

# ==============================================================================
# Stage 2: Runtime stage
# ==============================================================================
FROM python:3.14-slim AS runner

WORKDIR /app

# Set environment variables for secure and optimized container execution
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PATH="/app/.venv/bin:$PATH"

# Create non-root system group and user
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --shell /bin/false appuser

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY . .

# Create media and staticfiles directories and assign ownership to non-root user
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appgroup /app

# Execute collectstatic to compile WhiteNoise asset cache
RUN SECRET_KEY="dummy-build-key-for-collectstatic" \
    DATABASE_URL="sqlite:////tmp/dummy.db" \
    python manage.py collectstatic --noinput

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Run Gunicorn production WSGI server
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-"]
