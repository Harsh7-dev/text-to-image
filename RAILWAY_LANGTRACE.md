# LangTrace with Railway Deployment

This guide shows how to use LangTrace for observability in your Railway-deployed text-to-image application.

## 🚀 Quick Setup

### **1. Get LangTrace API Key**
1. Sign up at [LangTrace.ai](https://langtrace.ai)
2. Create a new project
3. Copy your API key

### **2. Add Environment Variable to Railway**
1. Go to your Railway project dashboard
2. Navigate to the "Variables" tab
3. Add a new variable:
   - **Name**: `LANGTRACE_API_KEY`
   - **Value**: Your LangTrace API key

### **3. Deploy to Railway**
```bash
# Push your code to GitHub
git add .
git commit -m "Add LangTrace observability"
git push origin main

# Railway will automatically deploy
```

## 📊 What LangTrace Tracks

### **Model Interactions**
- **Model**: `stability-ai/sdxl`
- **Prompts**: Input text (for analysis)
- **Responses**: Generated image URLs
- **Success/Failure**: Generation status
- **Performance**: Response times

### **Attributes Tracked**
```python
# Each image generation request tracks:
{
    "model": "stability-ai/sdxl",
    "prompt": "user input text",
    "platform": "railway",
    "success": true/false,
    "output_url": "generated image URL",
    "model_version": "model version hash"
}
```

## 🔍 Viewing LangTrace Data

### **1. LangTrace Dashboard**
- Visit [LangTrace.ai](https://langtrace.ai)
- Navigate to your project
- View real-time traces and metrics

### **2. Key Metrics Available**
- **Request Volume**: Number of image generations
- **Success Rate**: Percentage of successful generations
- **Response Time**: Average generation time
- **Cost Analysis**: API usage costs
- **Prompt Analysis**: Most common prompts

### **3. Trace Details**
- **Request Timeline**: Step-by-step execution
- **Error Analysis**: Failed request details
- **Performance Bottlenecks**: Slow operations
- **Model Performance**: Success rates by model

## 💡 Benefits for Railway

### **Real-time Monitoring**
- **No infrastructure setup** required
- **Automatic data collection** from your app
- **Instant insights** into model performance

### **Cost Optimization**
- **Track API usage** and costs
- **Identify expensive requests**
- **Optimize prompt strategies**

### **Debugging**
- **Trace failed requests** end-to-end
- **Identify model issues** quickly
- **Monitor user experience**

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
LANGTRACE_API_KEY=your-langtrace-api-key

# Optional (already set by Railway)
REPLICATE_API_TOKEN=your-replicate-token
```

### **Code Integration**
The LangTrace integration is already added to your `app/main.py`:

```python
# Initialize LangTrace
langtrace = LangTrace(
    api_key=os.getenv("LANGTRACE_API_KEY"),
    project_name="text-to-image-railway"
)

# Trace model interactions
with langtrace.trace("replicate_sdxl") as span:
    span.set_attributes({
        "model": "stability-ai/sdxl",
        "prompt": prompt.text,
        "platform": "railway"
    })
    # ... model call ...
```

## 📈 Monitoring Your App

### **Daily Checks**
1. **Success Rate**: Should be >95%
2. **Response Time**: Should be <30 seconds
3. **Error Patterns**: Check for common failures
4. **Cost Trends**: Monitor API usage

### **Weekly Analysis**
1. **Popular Prompts**: Most requested image types
2. **Performance Trends**: Response time patterns
3. **Cost Optimization**: Identify expensive requests
4. **User Behavior**: Peak usage times

## 🚨 Troubleshooting

### **LangTrace Not Working**
```bash
# Check if API key is set
echo $LANGTRACE_API_KEY

# Check Railway logs
railway logs

# Verify in Railway dashboard
# Variables tab → LANGTRACE_API_KEY
```

### **No Data in Dashboard**
1. **Wait 5-10 minutes** for data to appear
2. **Check API key** is correct
3. **Verify project name** matches
4. **Test with a simple request**

### **High Error Rates**
1. **Check Replicate API status**
2. **Verify API token** is valid
3. **Check prompt length** limits
4. **Monitor Railway resources**

## 🔮 Future Enhancements

### **Advanced Features**
- **Custom metrics** for business KPIs
- **Alerting** for high error rates
- **Cost alerts** for budget management
- **Performance benchmarking**

### **Integration Options**
- **Slack notifications** for errors
- **Email reports** for daily summaries
- **Custom dashboards** for stakeholders
- **API access** for custom analytics

## 📚 Resources

- [LangTrace Documentation](https://docs.langtrace.ai/)
- [Railway Documentation](https://docs.railway.app/)
- [Replicate API Documentation](https://replicate.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🎯 Next Steps

1. **Deploy to Railway** with LangTrace
2. **Generate some test images** to see data
3. **Explore the LangTrace dashboard**
4. **Set up monitoring alerts** (optional)
5. **Analyze performance patterns**

Your Railway app will now have enterprise-grade AI/ML observability without any complex infrastructure setup! 