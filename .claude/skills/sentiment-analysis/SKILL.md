---
name: sentiment-analysis
description: Advanced sentiment analysis toolkit for culinary tourism reviews with bilingual Thai-English support, emotional keyword detection, and cultural context interpretation for restaurant business intelligence.
license: MIT
---

# Culinary Sentiment Analysis Toolkit

Specialized sentiment analysis system designed for Chiang Mai restaurant reviews with bilingual processing capabilities and cultural context awareness.

## Core Capabilities

### Emotional Keyword Analysis
- **Positive Emotions**: Cozy, Inviting, Bustling, Romantic, Uplifting, Charming, Luxurious, Relaxing, Nostalgic, Joyful, Vibrant, Hospitable
- **Neutral/Descriptive**: Intimate (Small and private), Mellow, Formal
- **Negative Emotions**: Stuffy, Chaotic, Unwelcoming, Dull, Tense, Sterile, Overwhelming, Dreary

### Bilingual Processing
- Thai language emotional expression recognition
- English review sentiment preservation
- Cross-cultural sentiment translation
- Regional dialect consideration for Northern Thailand

## Usage Patterns

### Basic Sentiment Analysis
```python
from sentiment_analysis import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze_review(
    text="ร้านอาหารนี้บรรยากาศอบอุ่นและสบายๆ อาหารอร่อยมาก",
    language='th',
    context='restaurant'
)

print(f"Sentiment Score: {result.sentiment_score}")
print(f"Emotional Keywords: {result.emotional_keywords}")
print(f"Cultural Context: {result.cultural_interpretation}")
```

### Batch Processing for Business Intelligence
```python
# Analyze multiple reviews for business insights
business_analyzer = BusinessSentimentIntelligence()
insights = business_analyzer.analyze_restaurant_reviews(
    reviews_file='chiang_mai_reviews.csv',
    emotional_keywords=True,
    cultural_context=True,
    business_recommendations=True
)

# Generate actionable business report
report = business_analyzer.generate_business_report(insights)
```

### Cultural Context Analysis
```python
cultural_analyzer = CulturalContextAnalyzer()

# Analyze Thai dining culture expressions
cultural_insights = cultural_analyzer.analyze_cultural_expressions(
    reviews=thai_reviews,
    cultural_context='northern_thai_dining'
)

# Compare tourist vs local perspectives
comparison = cultural_analyzer.compare_customer_segments(
    tourist_reviews=tourist_reviews,
    local_reviews=local_reviews
)
```

## Advanced Features

### Emotional Trend Mapping
```python
trend_analyzer = EmotionalTrendAnalyzer()

# Track emotional changes over time
trends = trend_analyzer.analyze_temporal_sentiment(
    reviews=reviews_with_dates,
    time_window='monthly',
    emotional_categories=['positive', 'negative', 'neutral']
)

# Identify seasonal patterns in customer sentiment
seasonal_patterns = trend_analyzer.detect_seasonal_variations(
    sentiment_data=trends,
    location='chiang_mai'
)
```

### Competitive Intelligence
```python
competitive_analyzer = CompetitiveSentimentAnalysis()

# Benchmark against competitors
competitive_position = competitive_analyzer.benchmark_restaurant(
    target_restaurant_data=restaurant_data,
    competitor_data=competitor_list,
    emotional_dimensions=True
)

# Identify unique emotional positioning
positioning = competitive_analyzer.identify_emotional_niche(
    sentiment_profile=restaurant_sentiment,
    market_analysis=competitor_data
)
```

## Configuration

### Emotional Keyword Customization
```python
# Customize emotional keywords for specific cuisine types
thai_cuisine_keywords = {
    'positive': ['harmonious', 'authentic', 'aromatic', 'balanced', 'comforting'],
    'cultural_specific': ['sanuk', 'sabai sabai', 'nam jai', 'kreng jai'],
    'negative': ['bland', 'too sweet', 'lacking depth', 'inauthentic']
}

analyzer = SentimentAnalyzer(custom_keywords=thai_cuisine_keywords)
```

### Cultural Context Parameters
```python
# Configure for Chiang Mai specific context
chiang_mai_config = {
    'regional_dialects': ['kham muang', 'central thai'],
    'tourist_expectations': ['authenticity', 'hospitality', 'atmosphere'],
    'local_preferences': ['family-style', 'spice_levels', 'freshness'],
    'cultural_values': ['respect', 'community', 'tradition']
}

cultural_analyzer = CulturalContextAnalyzer(config=chiang_mai_config)
```

## Output Formats

### Business Intelligence Report
```python
# Generate comprehensive business report
business_report = analyzer.generate_business_report(
    sentiment_data=analysis_results,
    format='executive_dashboard',
    include_recommendations=True,
    financial_projections=True
)
```

### Export Capabilities
- **Executive Summary**: High-level insights for stakeholders
- **Detailed Analysis**: Comprehensive emotional breakdown
- **Action Items**: Specific improvement recommendations
- **Competitive Intelligence**: Market positioning analysis
- **Financial Impact**: ROI projections for improvements

## Integration Examples

### Web Application Integration
```python
# API endpoint for real-time sentiment analysis
@app.route('/analyze-review', methods=['POST'])
def analyze_review():
    review_data = request.json
    result = sentiment_analyzer.analyze_review(
        text=review_data['text'],
        language=review_data['language'],
        context='restaurant'
    )
    return jsonify(result)
```

### Database Integration
```python
# Store sentiment analysis results
def store_sentiment_analysis(restaurant_id, review_text, analysis_result):
    db_connection.execute("""
        INSERT INTO sentiment_analysis
        (restaurant_id, review_text, sentiment_score, emotional_keywords, cultural_context)
        VALUES (?, ?, ?, ?, ?)
    """, (restaurant_id, review_text, analysis_result.score,
          json.dumps(analysis_result.keywords), analysis_result.cultural_context))
```

## Best Practices

### Data Quality Assurance
- Validate input text for emotional content
- Handle mixed-language reviews appropriately
- Ensure cultural context accuracy
- Validate business insight applicability

### Performance Optimization
- Batch process multiple reviews for efficiency
- Cache sentiment models for faster processing
- Optimize emotional keyword matching algorithms
- Use parallel processing for large datasets

### Cultural Sensitivity
- Respect cultural nuances in emotional expression
- Consider regional differences in Thai language
- Avoid Western bias in sentiment interpretation
- Validate findings with local cultural experts

## Troubleshooting

### Common Issues
1. **Language Detection Errors**: Ensure proper language identification for mixed reviews
2. **Cultural Misinterpretation**: Validate cultural context with local experts
3. **Keyword Overfitting**: Regularly update emotional keyword lists
4. **Bias in Analysis**: Regularly audit for cultural or demographic biases

### Performance Optimization
- Use batch processing for large review datasets
- Implement caching for frequently analyzed restaurant data
- Optimize database queries for sentiment analysis results
- Consider cloud-based processing for large-scale analysis

Focus on extracting actionable business intelligence from customer sentiment while respecting cultural context and providing accurate emotional analysis for restaurant improvement strategies.