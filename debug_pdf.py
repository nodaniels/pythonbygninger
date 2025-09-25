#!/usr/bin/env python3
"""
Debug script to analyze PDF text extraction
Shows all text found in PDFs to help debug room detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import PDFParser

def analyze_pdf(pdf_path, floor_name):
    """Analyze a single PDF file"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {floor_name}")
    print(f"File: {os.path.basename(pdf_path)}")
    print(f"{'='*60}")
    
    parser = PDFParser(pdf_path)
    if not parser.load_pdf():
        print("❌ Failed to load PDF")
        return
    
    try:
        # Get text content with detailed analysis
        page = parser.doc[0]
        text_dict = page.get_text("dict")
        
        all_texts = []
        
        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                        
                    font_size = span["size"]
                    bbox = span["bbox"]
                    
                    # Calculate normalized font size (same logic as in parser)
                    page_rect = page.rect
                    reference_size = 595 * 842
                    actual_size = page_rect.width * page_rect.height
                    size_scale_factor = (actual_size / reference_size) ** 0.5
                    normalized_font_size = font_size / size_scale_factor
                    
                    all_texts.append({
                        'text': text,
                        'font_size': font_size,
                        'normalized_font_size': normalized_font_size,
                        'bbox': bbox,
                        'is_room': parser.is_room_text(text, font_size, normalized_font_size),
                        'is_entrance': parser.is_entrance_text(text)
                    })
        
        # Sort by font size (largest first)
        all_texts.sort(key=lambda x: x['font_size'], reverse=True)
        
        print(f"Found {len(all_texts)} text elements")
        print("\nTop text elements by font size:")
        print("-" * 80)
        
        for i, item in enumerate(all_texts[:30]):  # Show top 30
            status = ""
            if item['is_room']:
                status = " [ROOM]"
            elif item['is_entrance']:
                status = " [ENTRANCE]"
            
            norm_size = item.get('normalized_font_size', 0)
            print(f"{i+1:2d}. '{item['text']:<20}' size:{item['font_size']:4.1f} norm:{norm_size:4.1f}{status}")
        
        # Count classifications
        rooms = [t for t in all_texts if t['is_room']]
        entrances = [t for t in all_texts if t['is_entrance']]
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total texts: {len(all_texts)}")
        print(f"   Detected rooms: {len(rooms)}")
        print(f"   Detected entrances: {len(entrances)}")
        
        if rooms:
            print(f"\n🏠 ROOMS FOUND:")
            for room in rooms[:10]:  # Show first 10 rooms
                print(f"   • {room['text']} (size: {room['font_size']:.1f})")
        
        if entrances:
            print(f"\n🚪 ENTRANCES FOUND:")
            for entrance in entrances:
                print(f"   • {entrance['text']} (size: {entrance['font_size']:.1f})")
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
    finally:
        parser.close()

def main():
    """Main debug function"""
    print("🔍 PDF Text Analysis Debug Tool")
    
    # Path to PDF files
    base_path = os.path.dirname(__file__)
    bygninger_dir = os.path.join(base_path, "bygninger")
    
    if not os.path.exists(bygninger_dir):
        print(f"❌ Error: bygninger directory not found at {bygninger_dir}")
        return
    
    # Scan all buildings
    for building_name in os.listdir(bygninger_dir):
        building_path = os.path.join(bygninger_dir, building_name)
        
        if os.path.isdir(building_path):
            print(f"\n{'='*80}")
            print(f"BUILDING: {building_name.upper()}")
            print(f"{'='*80}")
            
            # Get all PDF files in building
            pdf_files = [f for f in os.listdir(building_path) if f.endswith('.pdf')]
            
            if not pdf_files:
                print(f"❌ No PDF files found in {building_name}")
                continue
                
            pdf_files.sort()
            
            for filename in pdf_files:
                pdf_path = os.path.join(building_path, filename)
                floor_name = os.path.splitext(filename)[0]  # Remove .pdf extension
                
                analyze_pdf(pdf_path, floor_name)
    
    print(f"\n{'='*60}")
    print("Analysis complete!")
    print("If rooms are missing, check the is_room_text() patterns.")

if __name__ == "__main__":
    main()
