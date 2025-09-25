# Building Navigation Prototype

En Python-prototype af building navigation appen i iPhone-format.

## Features
- 🔍 Søg efter lokaler på tværs af alle etager
- 🏢 Automatisk visning af korrekt etage
- 🟢 Grøn markering af søgt lokale
- 🟠 Orange markering af nærmeste indgang (altid fra stueetagen)
- 📱 iPhone-lignende interface (375x812px)
- 🎯 Eksakt match search (case-insensitive)

## Installation

1. **Installer Python** (3.8 eller nyere)
2. **Installer dependencies:**
   ```bash
   pip install PyMuPDF Pillow
   ```

## Brug

```bash
python main.py
```

## Filstruktur
```
prototype/
├── main.py              # Hovedapplikation (iPhone GUI)
├── pdf_parser.py        # PDF parsing og tekstudtrækning
├── requirements.txt     # Python dependencies
└── README.md           # Denne fil
```

## Hvordan det virker

1. **PDF Loading:** Indlæser alle 3 PDF-filer fra porcelaenshaven mappen
   - Stueetage: `stueetage_kl_9_cbs_porcelanshaven_21.pdf`
   - 1. sal: `porcelaenshaven_1._sal_pdf_1 (1).pdf`
   - 2. sal: `121128-02_2_sal_kl_9_cbs_porcelaenshaven.pdf`

2. **Text Extraction:** Bruger PyMuPDF til at udtrække tekst med præcise koordinater

3. **Room Search:** Søger på tværs af alle etager med eksakt match (case-insensitive)

4. **Visual Display:** 
   - Viser PDF fra den etage hvor lokalet er fundet
   - Grøn prik markerer lokalet
   - Orange prik viser nærmeste indgang fra stueetagen

## Konvertering til React Native

Denne prototype er designet til nem konvertering:

### Forretningslogik → JavaScript
```python
# Python
def search_room(self, room_query):
    room_query = room_query.upper().strip()
    # search logic...
```

```javascript
// React Native
const searchRoom = (roomQuery) => {
  const normalizedQuery = roomQuery.toUpperCase().trim();
  // same search logic...
};
```

### PDF Rendering → React Native PDF
```python
# Python (PyMuPDF)
pdf_image = parser.render_pdf_as_image(scale=2.0)
```

```javascript
// React Native (react-native-pdf)
<Pdf
  source={{uri: pdfPath}}
  onLoadComplete={(numberOfPages,filePath) => {
    // PDF loaded
  }}
/>
```

### Coordinate Mapping → Same Logic
```python
# Python
norm_x = x / page_rect.width
norm_y = y / page_rect.height
```

```javascript
// React Native (same approach)
const normX = x / pageWidth;
const normY = y / pageHeight;
```

### GUI Components → React Native
```python
# Python (Tkinter)
search_entry = tk.Entry(...)
search_btn = ttk.Button(...)
```

```jsx
// React Native
<TextInput 
  value={searchQuery}
  onChangeText={setSearchQuery}
/>
<TouchableOpacity onPress={handleSearch}>
  <Text>Søg</Text>
</TouchableOpacity>
```

## Test Cases

Prøv at søge efter:
- Lokaler på stueetage
- Lokaler på 1. sal  
- Lokaler på 2. sal
- Ikke-eksisterende lokaler

Appen vil automatisk:
- Finde den rigtige etage
- Vise lokalet med grøn markering
- Vise nærmeste indgang med orange markering
