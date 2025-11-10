# -*- coding: utf-8 -*-
"""
Analyze 03:39 output for language consistency
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import json

def analyze_output():
    # Load the reviews.json file
    with open('outputs/20251111_033908_28117d3d/reviews.json', 'r', encoding='utf-8') as f:
        reviews = json.load(f)

    print('ANALYZING OUTPUT: 20251111_033908_28117d3d')
    print('=' * 50)
    print(f'Place: Khao Soi Nimman (Thai restaurant)')
    print(f'Total reviews: {len(reviews)}')
    print(f'Target: 2000 reviews')
    print(f'Language: en')
    print()

    # Language consistency analysis
    english_count = 0
    thai_count = 0
    empty_count = 0
    pages_with_thai = {}

    for review in reviews:
        text = review.get('review_text', '')
        page = review.get('page_number', 0)

        if not text.strip():
            empty_count += 1
        else:
            # Check for Thai characters
            has_thai = any('\u0E00' <= char <= '\u0E7F' for char in text)
            if has_thai:
                thai_count += 1
                if page not in pages_with_thai:
                    pages_with_thai[page] = 0
                pages_with_thai[page] += 1
            else:
                english_count += 1

    total = len(reviews)
    en_pct = (english_count / total * 100) if total > 0 else 0
    thai_pct = (thai_count / total * 100) if total > 0 else 0

    print('LANGUAGE CONSISTENCY RESULTS:')
    print(f'English reviews: {english_count} ({en_pct:.1f}%)')
    print(f'Thai reviews: {thai_count} ({thai_pct:.1f}%)')
    print(f'Empty text: {empty_count}')
    print(f'Total pages with Thai content: {len(pages_with_thai)}')

    print()
    print('PAGES WITH THAI CONTENT:')
    for page in sorted(pages_with_thai.keys()):
        print(f'  Page {page}: {pages_with_thai[page]} Thai reviews')

    print()
    print('DRIFT ANALYSIS:')
    sorted_pages = sorted(pages_with_thai.keys())
    if sorted_pages:
        first_thai_page = sorted_pages[0]
        last_thai_page = sorted_pages[-1]
        print(f'First Thai content appears at page: {first_thai_page}')
        print(f'Last Thai content appears at page: {last_thai_page}')
        print(f'Thai content spread: {last_thai_page - first_thai_page} pages')
    else:
        print('No Thai content found!')

    print()
    print('COMPARISON WITH OTHER RESULTS:')
    print('-' * 40)
    print('Previous problematic (03:19): 90.1% English, 197 Thai reviews')
    print('Enhanced 1000-review (03:31): 99.8% English, 2 Thai reviews')
    print('This 2000-review (03:39):', f'{en_pct:.1f}% English, {thai_count} Thai reviews')

    if en_pct >= 98:
        print('EXCELLENT: Nearly perfect consistency!')
    elif en_pct >= 95:
        print('GOOD: Strong English consistency')
    elif en_pct >= 90:
        print('ACCEPTABLE: Mostly English')
    else:
        print('PROBLEM: High non-English content')

    print()
    print('VERDICT:')
    if en_pct >= 95 and thai_count <= 10:
        print('SUCCESS: Language fix is working!')
    elif en_pct >= 90:
        print('IMPROVED: Better than original but room for improvement')
    else:
        print('FAILED: Language issue persists')

    # Show sample Thai reviews if any
    if thai_count > 0:
        print()
        print('SAMPLE THAI REVIEWS:')
        thai_samples = [r for r in reviews if r.get('review_text', '') and any('\u0E00' <= char <= '\u0E7F' for char in r['review_text'])][:3]

        for i, review in enumerate(thai_samples, 1):
            author = review.get('author_name', 'Unknown')[:30]
            text = review.get('review_text', '')[:100]
            rating = review.get('rating', 0)
            page = review.get('page_number', 0)
            print(f'{i}. Page {page}: {author} ({rating} stars)')
            print(f'   \"{text}...\"')
            print()

    return {
        'total_reviews': total,
        'english_count': english_count,
        'thai_count': thai_count,
        'english_pct': en_pct,
        'thai_pct': thai_pct,
        'pages_with_thai': len(pages_with_thai)
    }

if __name__ == "__main__":
    results = analyze_output()
    print(f'Analysis complete: {results}')