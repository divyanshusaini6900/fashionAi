# Instructions for Using FashionModelingAI with Postman

## आपका FashionModelingAI प्रोजेक्ट तैयार है! (Your FashionModelingAI Project is Ready!)

आपने सफलतापूर्वक FashionModelingAI प्रोजेक्ट सेटअप कर लिया है और अब इसे Postman के साथ टेस्ट कर सकते हैं।

## English Instructions

### 1. Start the Application Server
The application server is already running on `http://127.0.0.1:8000`

If you need to restart it, use:
```bash
python -m uvicorn app.main:app --reload
```

### 2. Import Postman Collection
1. Open Postman
2. Click "Import" in the top left corner
3. Select the following files from the `postman` folder:
   - `FashionModelingAI_Collection.json`
   - `FashionModelingAI_Environment.json`
4. Click "Import"

### 3. Test the API
1. In Postman, select "FashionModelingAI Local" from the environment dropdown (top right)
2. Select the "Generate Fashion Content" request from the collection
3. In the "Body" tab:
   - Click "Select Files" next to `frontside` and choose an image from `tests/test_data/`
   - Fill in the required fields:
     - `text`: "woman dress, stylish, elegant, event wear"
     - `username`: "test_user"
     - `product`: "dress"
4. Click "Send"

### 4. View Results
The API will return URLs to:
- Generated images
- Excel report
- Additional variations

You can open these URLs in your browser to view the generated content.

## हिंदी निर्देश (Hindi Instructions)

### 1. एप्लिकेशन सर्वर स्टार्ट करें
एप्लिकेशन सर्वर पहले से ही `http://127.0.0.1:8000` पर चल रहा है

यदि आपको इसे पुनः आरंभ करने की आवश्यकता है, तो उपयोग करें:
```bash
python -m uvicorn app.main:app --reload
```

### 2. Postman Collection आयात करें
1. Postman खोलें
2. शीर्ष बाईं ओर "Import" पर क्लिक करें
3. `postman` फ़ोल्डर से निम्नलिखित फ़ाइलों का चयन करें:
   - `FashionModelingAI_Collection.json`
   - `FashionModelingAI_Environment.json`
4. "Import" पर क्लिक करें

### 3. API का परीक्षण करें
1. Postman में, वातावरण ड्रॉपडाउन (शीर्ष दाएं) से "FashionModelingAI Local" का चयन करें
2. संग्रह से "Generate Fashion Content" अनुरोध का चयन करें
3. "Body" टैब में:
   - `frontside` के बगल में "Select Files" पर क्लिक करें और `tests/test_data/` से एक छवि चुनें
   - आवश्यक फ़ील्ड भरें:
     - `text`: "woman dress, stylish, elegant, event wear"
     - `username`: "test_user"
     - `product`: "dress"
4. "Send" पर क्लिक करें

### 4. परिणाम देखें
API आपको ये URLs लौटाएगा:
- उत्पन्न छवियाँ
- एक्सेल रिपोर्ट
- अतिरिक्त विविधताएँ

आप इन URLs को अपने ब्राउज़र में खोलकर उत्पन्न सामग्री देख सकते हैं।

## Troubleshooting / समस्या निवारण

If you encounter any issues:
- Make sure the server is running on `http://127.0.0.1:8000`
- Check that all required API keys are set in your `.env` file
- Ensure image files are in JPG format

यदि आपको कोई समस्या आती है:
- सुनिश्चित करें कि सर्वर `http://127.0.0.1:8000` पर चल रहा है
- जांचें कि आपकी `.env` फ़ाइल में सभी आवश्यक API कुंजियाँ सेट हैं
- सुनिश्चित करें कि छवि फ़ाइलें JPG प्रारूप में हैं

## Additional Resources / अतिरिक्त संसाधन

- Detailed setup instructions: `HOW_TO_RUN.md`
- Project overview: `PROJECT_SUMMARY.md`
- Postman instructions: `postman/POSTMAN_INSTRUCTIONS.md`