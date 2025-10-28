# Database Schema Design

## Overview
This document outlines the database schema for the BIG API full-stack application using PostgreSQL/Vercel Postgres.

## Tables

### 1. users
Stores user account information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'free', -- free, starter, pro, enterprise
    credits INTEGER DEFAULT 100,
    stripe_customer_id VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id);
```

### 2. api_keys
Stores API keys for each user.

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL, -- 'big_live_' or 'big_test_'
    key_hash VARCHAR(255) NOT NULL, -- hashed full key
    key_preview VARCHAR(50) NOT NULL, -- last 4 chars for display
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    permissions JSONB DEFAULT '{"all": true}' -- future: scope restrictions
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
```

### 3. usage_logs
Detailed usage tracking for billing and analytics.

```sql
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    request_id VARCHAR(100),
    provider VARCHAR(50) NOT NULL,
    credits_used INTEGER NOT NULL,
    task_count INTEGER NOT NULL,
    success_count INTEGER NOT NULL,
    failed_count INTEGER NOT NULL,
    prompt_tokens INTEGER,
    response_time_ms INTEGER,
    error_message TEXT,
    metadata JSONB, -- stores task details, model params, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX idx_usage_logs_provider ON usage_logs(provider);
```

### 4. credit_transactions
Tracks all credit purchases and usage.

```sql
CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'purchase', 'usage', 'refund', 'bonus'
    amount INTEGER NOT NULL, -- positive for purchase, negative for usage
    balance_after INTEGER NOT NULL,
    description TEXT,
    stripe_payment_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_type ON credit_transactions(type);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at);
```

### 5. subscriptions
Tracks user subscriptions for recurring billing.

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    plan VARCHAR(50) NOT NULL, -- starter, pro, enterprise
    status VARCHAR(50) NOT NULL, -- active, canceled, past_due
    credits_per_month INTEGER NOT NULL,
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

### 6. webhook_events
Stores webhook events for debugging and processing.

```sql
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    source VARCHAR(50) NOT NULL, -- 'stripe', 'other'
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_webhook_events_event_id ON webhook_events(event_id);
CREATE INDEX idx_webhook_events_processed ON webhook_events(processed);
```

## Redis Schema (Vercel KV)

### API Key Cache
```
Key: api_key:{key_hash}
Value: JSON stringified user data
TTL: 1 hour
```

### Rate Limiting
```
Key: rate_limit:{user_id}:{window}
Value: request count
TTL: based on window (1min, 1hour, 1day)
```

### User Session
```
Key: session:{session_id}
Value: JSON stringified session data
TTL: 7 days
```

## Pricing Tiers

### Free Tier
- 100 credits on signup
- Rate limit: 10 requests/minute
- Access to basic providers

### Starter ($29/month)
- 5,000 credits/month
- Rate limit: 60 requests/minute
- Access to all providers
- Email support

### Pro ($99/month)
- 25,000 credits/month
- Rate limit: 120 requests/minute
- Priority access
- Dedicated support
- Custom integrations

### Enterprise (Custom)
- Custom credit allocation
- Custom rate limits
- SLA guarantee
- Dedicated account manager
- White-label options

## Credit Costs Summary

| Provider | Credits | Quality |
|----------|---------|---------|
| DALL-E 3 | 10 | High |
| FLUX Kontext | 8 | High |
| Seedream 4 | 8 | High |
| Imagen 4 | 9 | High |
| Imagen 4 Ultra | 12 | Ultra |
| GPT Image 1 | 11 | Ultra |
| Ideogram V3 | 9 | High |
| Minimax | 7 | Medium |
| Seedream 3 | 7 | Medium |
| FLUX Dev | 6 | Medium |
| Imagen 3 | 6 | Medium |
| Qwen-Image | 6 | Medium |
| Gemini | 5 | Medium |
| Reve | 5 | Medium |
| Imagen 4 Fast | 7 | Medium |
