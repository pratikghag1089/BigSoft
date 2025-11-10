# 🚀 Real Business Mode - Setup Guide

## Transform Your AI Entrepreneur from Simulation to REAL Business!

With Razorpay and DigitalOcean, your AI can now:
- ✅ Deploy REAL services to the cloud
- ✅ Accept REAL payments from customers
- ✅ Track REAL revenue and costs
- ✅ Manage REAL infrastructure
- ✅ Build a REAL profitable business!

---

## 📋 Prerequisites

### 1. Razorpay Account (Payment Gateway)

**Sign Up:**
1. Go to https://razorpay.com/
2. Click "Sign Up" (free to start)
3. Complete KYC verification (required for India)
4. Activate your account

**Get API Keys:**
1. Login to https://dashboard.razorpay.com/
2. Go to **Settings** → **API Keys**
3. Generate Test Keys first (for testing)
4. Later, generate Live Keys (for real business)
5. Copy your:
   - `Key ID` (starts with `rzp_test_` or `rzp_live_`)
   - `Key Secret` (keep this SECRET!)

**Important:**
- Test mode: Free, fake payments for testing
- Live mode: Real payments, real money (requires KYC)

### 2. DigitalOcean Account (Cloud Hosting)

**Sign Up:**
1. Go to https://www.digitalocean.com/
2. Sign up (get $200 free credit for 60 days!)
3. Add payment method (credit card required)
4. Verify email

**Get API Token:**
1. Login to https://cloud.digitalocean.com/
2. Go to **API** → **Tokens/Keys**
3. Click **Generate New Token**
4. Name it: `AI-Entrepreneur-System`
5. Select **Write** access (full access)
6. Copy the token (you only see it once!)

**Important:**
- Keep token secret!
- Each droplet costs ~$6/month
- You can delete droplets anytime to stop costs

### 3. SSH Key (Optional but Recommended)

**Generate SSH Key:**
```bash
# Generate key pair
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_rsa.pub
```

**Add to DigitalOcean:**
1. Go to **Settings** → **Security** → **SSH Keys**
2. Click **Add SSH Key**
3. Paste your public key
4. Note the SSH Key ID

---

## 🔧 Configuration

### Step 1: Install Dependencies

```bash
cd ~/BigSoft
source venv/bin/activate
pip install -r requirements.txt
```

This installs:
- `razorpay` - Payment processing SDK
- All other dependencies

### Step 2: Configure Environment

Copy the example configuration:

```bash
cp .env.real_business_example .env
```

Edit `.env` with your credentials:

```bash
nano .env
```

**Fill in these CRITICAL values:**

```env
# Enable real business mode
REAL_BUSINESS_MODE=true
USE_REAL_PAYMENTS=true
USE_REAL_DEPLOYMENT=true

# Razorpay (from dashboard.razorpay.com)
RAZORPAY_ENABLED=true
RAZORPAY_KEY_ID=rzp_test_XXXXXXXXXXXXXXXX    # Your actual key
RAZORPAY_KEY_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX # Your actual secret

# DigitalOcean (from cloud.digitalocean.com)
DIGITALOCEAN_ENABLED=true
DIGITALOCEAN_API_TOKEN=dop_v1_XXXXXXXXXXXXXXXXXXXXXXXXXXXX # Your actual token
DIGITALOCEAN_SSH_KEY_ID=12345678            # Optional, your SSH key ID
DIGITALOCEAN_DEFAULT_REGION=blr1            # Bangalore, India (or sgp1, nyc1, etc.)

# Business settings
INITIAL_CAPITAL=1000.0
RISK_TOLERANCE=0.7
```

**⚠️ IMPORTANT:**
- Start with TEST mode first (Razorpay test keys)
- Test everything before switching to LIVE mode
- Keep your secrets SECRET - don't commit to git!

### Step 3: Test Configuration

```bash
# Test Razorpay connection
python -c "
from src.business.payment_gateway import razorpay_gateway
balance = razorpay_gateway.get_balance()
print('Razorpay connected:', balance)
"

# Test DigitalOcean connection
python -c "
from src.deployment.digitalocean_deployer import digitalocean_deployer
droplets = digitalocean_deployer.list_droplets()
print('DigitalOcean connected, droplets:', len(droplets))
"
```

If both work, you're ready! 🎉

---

## 🚀 Running in Real Business Mode

### Start the System

```bash
# Start Ollama first
ollama serve

# In another terminal, start the AI entrepreneur
cd ~/BigSoft
source venv/bin/activate
python main_ui.py
```

**Open browser:** http://localhost:8000

### What Happens Now

1. **AI Identifies Opportunity** (same as before)
   ```
   🧠 AI: Found opportunity "AI Content API"
   💰 Estimated revenue: $5,000
   💸 Estimated cost: $500
   ```

2. **AI Generates Code** (same as before)
   ```
   📁 Creating workspace: venture_5_ai_content_api/
   💻 Generating service code...
   ✅ Code generated: 250 lines
   ```

3. **🆕 AI Deploys to DigitalOcean** (NEW!)
   ```
   🌐 Creating droplet in Bangalore (blr1)...
   ✅ Droplet created: venture-5-ai-content-api (IP: 143.110.xxx.xxx)
   🚀 Deploying service...
   ✅ Service live at: http://143.110.xxx.xxx:8000
   💰 Real cost: $6/month
   ```

4. **🆕 AI Creates Payment Link** (NEW!)
   ```
   💳 Creating Razorpay payment link...
   ✅ Payment link: https://rzp.io/l/XXXXXXXX
   🇮🇳 Price: ₹415,000 ($5,000 USD)
   📊 Type: One-time payment
   ```

5. **🆕 AI Tracks Real Costs** (NEW!)
   ```
   📊 Real costs:
   - Droplet: $6/month
   - Total invested: $6
   💰 Available capital: $994
   ```

6. **Service is LIVE!** 🎉
   ```
   ✅ Service URL: http://143.110.xxx.xxx:8000
   ✅ Payment link: https://rzp.io/l/XXXXXXXX
   ✅ Workspace: agent_data/workspaces/venture_5_ai_content_api/
   ```

### What You Can Do

**Share the service:**
```bash
# Your service is live at the IP address!
curl http://143.110.xxx.xxx:8000
```

**Share the payment link:**
- Send payment link to potential customers
- They pay with credit/debit card, UPI, netbanking
- Money goes to your Razorpay account
- AI tracks real revenue automatically!

**Check real revenue:**
```bash
# The system automatically checks for payments
# Revenue is tracked in the database
```

---

## 💰 Payment Flow

### How Customers Pay

1. **Customer gets payment link:**
   ```
   https://rzp.io/l/XXXXXXXX
   ```

2. **Customer pays** (via Razorpay page):
   - Credit/Debit Card
   - UPI (Google Pay, PhonePe, etc.)
   - NetBanking
   - Wallets

3. **Money received:**
   - Goes to your Razorpay account
   - Razorpay takes 2% fee
   - You can withdraw to bank account

4. **AI tracks revenue:**
   ```
   💰 Payment received: ₹415,000 ($5,000)
   📊 Profit: $5,000 - $6 = $4,994
   ✅ Opportunity profitable!
   ```

### Withdraw Money

**Razorpay Dashboard:**
1. Login to https://dashboard.razorpay.com/
2. Go to **Settlements**
3. Money automatically transferred to your bank (T+2 days)
4. Or request instant settlement (small fee)

---

## 🌐 Deployment Details

### What Gets Deployed

**For each opportunity, the AI:**

1. **Creates a Droplet:**
   - Ubuntu 22.04 server
   - 1 CPU, 1GB RAM
   - Bangalore region (or your choice)
   - Public IP address
   - Cost: $6/month

2. **Deploys Your Service:**
   - Copies generated code
   - Installs Python & dependencies
   - Sets up systemd service
   - Configures nginx reverse proxy
   - Enables firewall

3. **Service is Live:**
   - Accessible via HTTP
   - Runs 24/7
   - Auto-restarts if crashes
   - Can add custom domain later

### Managing Droplets

**View all droplets:**
```python
from src.deployment.digitalocean_deployer import digitalocean_deployer
droplets = digitalocean_deployer.list_droplets()
for d in droplets:
    print(f"{d['name']}: {d['ip_address']} - {d['status']}")
```

**Delete a droplet** (stop paying):
```python
digitalocean_deployer.delete_droplet("droplet_id_here")
```

**Via Dashboard:**
- Go to https://cloud.digitalocean.com/droplets
- See all droplets
- Delete, resize, or backup anytime

---

## 💡 Real Business Example

### Complete Flow

**Day 1: AI Identifies Opportunity**
```
🧠 AI: "AI Resume Parser API" looks profitable
💰 Revenue potential: $3,000
💸 Estimated cost: $500
✅ Pursuing opportunity...
```

**Day 1: AI Builds & Deploys**
```
💻 Generating FastAPI service (200 lines)
📚 Creating API documentation
🌐 Deploying to DigitalOcean Bangalore
✅ Live at: http://143.110.25.xxx:8000
💳 Payment link: https://rzp.io/l/abc123
```

**Day 5: First Customer!**
```
🎉 Payment received: $99 (monthly subscription)
📧 Customer email: startup@example.com
✅ Profit so far: $99 - $6 = $93
```

**Day 15: More Customers**
```
👥 Total customers: 15
💰 Monthly revenue: $99 × 15 = $1,485
💸 Monthly costs: $6 (droplet)
✅ Monthly profit: $1,479
📈 ROI: 2,465%!
```

**Day 30: Scale Up**
```
🚀 AI sees high demand
💡 AI decides: Upgrade to larger droplet
🌐 Upgraded to 2CPU/4GB ($24/month)
📊 Can handle 100+ customers now
```

**Month 3: Real Business**
```
👥 Customers: 50
💰 Monthly revenue: $99 × 50 = $4,950
💸 Monthly costs: $24 (droplet) + $99 (payment fees) = $123
✅ Monthly profit: $4,827
💼 You have a real business!
```

---

## 🎯 Strategy: Simulation to Profit

### Phase 1: Test Mode (Week 1)

**Settings:**
```env
REAL_BUSINESS_MODE=true
USE_REAL_DEPLOYMENT=true
USE_REAL_PAYMENTS=false      # Keep payments simulated
RAZORPAY_KEY_ID=rzp_test_... # Use test keys
```

**Why:**
- Deploy to real cloud
- Test deployment process
- No real money at risk
- Learn the system

### Phase 2: Live Payments (Week 2)

**Settings:**
```env
REAL_BUSINESS_MODE=true
USE_REAL_DEPLOYMENT=true
USE_REAL_PAYMENTS=true       # Enable real payments!
RAZORPAY_KEY_ID=rzp_live_... # Use LIVE keys
```

**Why:**
- Accept real payments
- Small risk ($6/month per service)
- Real revenue possible
- Learn customer acquisition

### Phase 3: Scale (Month 2+)

**Strategy:**
- Let AI create multiple services
- Monitor which services get customers
- Terminate unprofitable services
- Scale profitable ones
- Reinvest profits

**Example:**
```
Month 1:
- AI deploys 5 services
- Cost: 5 × $6 = $30/month
- 2 services get customers
- Revenue: $200
- Profit: $170

Month 2:
- Terminate 3 unprofitable services
- Cost: 2 × $6 = $12/month
- Scale 2 profitable services
- Revenue: $800
- Profit: $788

Month 3:
- AI creates 3 new services (based on learnings)
- Total services: 5
- Cost: 5 × $12 = $60/month (larger droplets)
- Revenue: $3,500
- Profit: $3,440
```

---

## 🔒 Security & Best Practices

### Protect Your Credentials

**Never commit .env to git:**
```bash
# Make sure .env is in .gitignore
echo ".env" >> .gitignore
```

**Use environment variables:**
```bash
# On production server
export RAZORPAY_KEY_SECRET="your_secret"
export DIGITALOCEAN_API_TOKEN="your_token"
```

**Rotate keys regularly:**
- Regenerate API keys every 90 days
- Use different keys for test vs production

### Monitor Costs

**Set DigitalOcean alerts:**
1. Go to **Account** → **Billing**
2. Set up billing alerts
3. Get notified at $50, $100, $200

**Track Razorpay fees:**
- Standard: 2% per transaction
- Refunds: Full fee refunded
- Disputes: May incur fees

### Prevent Abuse

**Rate limiting:**
- Add rate limiting to deployed services
- Prevent API abuse
- Protect your droplet resources

**Customer verification:**
- Use Razorpay's KYC features
- Verify high-value transactions
- Monitor for fraud

---

## 📊 Monitoring & Analytics

### Dashboard Features

**Real-time visibility:**
- 🌐 Deployed services status
- 💰 Real payments received
- 📊 Actual profit/loss
- 💳 Customer count
- 🔴 Droplet health

### Check Real Revenue

**Via Python:**
```python
from src.business.real_business_executor import RealBusinessExecutor
from src.database.database import db_manager

with db_manager.session_scope() as session:
    executor = RealBusinessExecutor(session)

    # Check opportunity revenue
    opportunity = session.query(Opportunity).get(5)
    revenue = executor.check_real_revenue(opportunity)
    print(f"Real revenue: ${revenue['real_revenue']}")

    # Check account balance
    balance = executor.get_real_balance()
    print(f"Razorpay balance: ${balance}")
```

**Via Razorpay Dashboard:**
- Login to https://dashboard.razorpay.com/
- View all payments
- Download reports
- Track settlements

**Via DigitalOcean Dashboard:**
- Login to https://cloud.digitalocean.com/
- View all droplets
- Check bandwidth usage
- Monitor costs

---

## 🛠️ Troubleshooting

### "Razorpay API Error: Authentication Failed"

**Problem:** Wrong API keys

**Solution:**
```bash
# Check your keys
echo $RAZORPAY_KEY_ID
echo $RAZORPAY_KEY_SECRET

# Make sure they match dashboard.razorpay.com
# Test keys start with: rzp_test_
# Live keys start with: rzp_live_
```

### "DigitalOcean API Error: 401 Unauthorized"

**Problem:** Wrong or expired token

**Solution:**
```bash
# Regenerate token
# 1. Go to cloud.digitalocean.com/account/api/tokens
# 2. Delete old token
# 3. Create new token
# 4. Update .env
```

### "Droplet Creation Failed: Insufficient Balance"

**Problem:** No credits/money in DigitalOcean account

**Solution:**
```bash
# Add payment method or use free credit
# Go to cloud.digitalocean.com/account/billing
```

### "Payment Link Not Working"

**Problem:** Account not activated or KYC pending

**Solution:**
```bash
# Complete KYC on Razorpay
# 1. Login to dashboard.razorpay.com
# 2. Go to Settings → Account Activation
# 3. Submit required documents
# 4. Wait for approval (usually 24-48 hours)
```

---

## 🎓 Next Steps

### After Setup

1. **Test in simulation mode first:**
   ```bash
   # In .env
   REAL_BUSINESS_MODE=false
   ```

2. **Then enable test payments:**
   ```bash
   REAL_BUSINESS_MODE=true
   USE_REAL_PAYMENTS=false  # Still testing
   RAZORPAY_KEY_ID=rzp_test_...
   ```

3. **Deploy test service manually:**
   ```python
   from src.deployment.digitalocean_deployer import digitalocean_deployer
   result = digitalocean_deployer.create_droplet(name="test-venture")
   print(result)
   ```

4. **Once confident, go LIVE:**
   ```bash
   USE_REAL_PAYMENTS=true
   RAZORPAY_KEY_ID=rzp_live_...
   ```

5. **Monitor daily:**
   - Check dashboard
   - Review payments
   - Monitor costs
   - Adjust strategy

### Growing Your Business

- **Marketing:** Share payment links on social media
- **SEO:** Add custom domains to deployed services
- **Scale:** Upgrade droplets as needed
- **Automate:** Let AI handle everything
- **Reinvest:** Use profits to create more services

---

## 💬 Questions?

**Check logs:**
```bash
tail -f logs/entrepreneur_agent.log
```

**View in UI:**
http://localhost:8000 - See everything in real-time!

**Test components:**
```bash
# Test payment gateway
python -c "from src.business.payment_gateway import razorpay_gateway; print(razorpay_gateway.get_balance())"

# Test deployer
python -c "from src.deployment.digitalocean_deployer import digitalocean_deployer; print(digitalocean_deployer.list_droplets())"
```

---

## 🎉 You're Ready!

You now have everything needed to run a REAL AI-powered business:

✅ Payment processing (Razorpay)
✅ Cloud deployment (DigitalOcean)
✅ AI decision-making
✅ Autonomous operations
✅ Real revenue tracking
✅ Full transparency

**Time to make it profitable!** 🚀💰
