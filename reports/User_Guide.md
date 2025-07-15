# Conference Research App User Guide

This guide provides step-by-step instructions on how to use the **Conference Research App** to automate delegate information retrieval, biography generation, lead generation, and outreach.

---

## **BioGen Tab**

The **BioGen** tab is used to generate academic profiles by searching local files or querying the internet. Here, you can search for details such as names, universities, and research interests.

1. **API Configuration**: The app uses OpenAI GPT-4o-mini and Google Serper API for enhanced bio generation and web search capabilities.
2. **File Upload**: Upload CSV/XLSX files with required columns: 'Name', 'University' (or 'Affiliation')
   - **Security**: Files are automatically validated for size (max 50MB), type, and content
   - **Formats**: Supports .csv, .xlsx, and .xls file formats
   - **Validation**: Real-time feedback on file validation status
3. **Chunk Processing**: Process data in configurable chunks to manage API costs and rate limits
4. **Bio Generation**: AI-powered biography creation with automatic email extraction
5. **Export Options**: Download results as Excel files with generated bios and extracted emails

### **Enhanced Features:**
- ✅ **Automatic Retry**: API calls automatically retry on failure with intelligent backoff
- ✅ **File Validation**: Comprehensive security checks for uploaded files
- ✅ **Error Recovery**: Better error handling and user feedback
- ✅ **Token Management**: Optimized API usage for cost efficiency

---

## **RAG (Lead Generation) Tab**

The **RAG (Retrieve, Augment, Generate)** tab is used for lead generation and delegate filtering. You can search for conference participants based on their university affiliation, research interests, and more.

1. **Upload Article**: Upload a document such as a conference list or research article for analysis.
2. **Ask a Question**: You can type a query related to the uploaded document, such as "Can you give me a short summary of the conference participants?"

---

## **Outreach Tab**

The **Outreach** tab assists with drafting emails to conference delegates.

1. **Select a Template**: Pick one of the built-in templates. The selected text automatically populates the **Enter your email draft** box for further editing.
2. **Edit the Draft**: Modify the text, choose a tone and length, then submit.
3. **Click Enhance**: An improved version of the email appears in a new editable field.
4. **Copy the Output**: Press **Copy Enhanced Email** to show a block where you can copy the final text.

---

## **Desktop Research Tab**

The **Desktop Research** tab allows you to search for academic profiles by querying local files or performing an internet search.

1. **API Configuration**: Uses Groq API for enhanced internet search functionality
2. **Search Parameters**:
   - **Full Name**: Enter the complete name of the individual you're researching
   - **Research or Teaching Interest**: Add specific research interests for targeted results
   - **University**: Add the affiliated university for more precise results
3. **Data Sources**: Choose between **Local Files** or **Internet** for your search
4. **File Upload**: Upload CSV/XLSX files for local searching
   - **Flexible Column Support**: Automatically handles both 'University' and 'Affiliation' column names
   - **Data Validation**: Real-time validation of file format and required columns
   - **Error Handling**: Clear messages for missing or misnamed columns
5. **Enhanced Processing**: Improved data extraction and compatibility with various data sources

### **Recent Improvements:**
- ✅ **Column Flexibility**: Automatic handling of 'Affiliation' vs 'University' column variations
- ✅ **Better Compatibility**: Enhanced support for different CSV/XLSX formats
- ✅ **Improved Error Messages**: More descriptive feedback for data issues
- ✅ **Enhanced Data Processing**: Better extraction accuracy and error recovery

---

## **Security & File Upload Guidelines**

### **File Upload Security**
The Conference Research App now includes comprehensive file validation to ensure security and reliability:

- **Supported File Types**: Only CSV (.csv), Excel (.xlsx, .xls) files are accepted
- **File Size Limit**: Maximum 50MB per file to ensure optimal performance
- **Security Validation**: Files are automatically scanned for suspicious content and naming patterns
- **MIME Type Verification**: File content is verified to match the declared file extension

### **Best Practices for File Uploads**
1. **Use Clean Filenames**: Avoid special characters like `../`, `<>`, or other potentially harmful patterns
2. **Verify File Format**: Ensure your data is properly formatted with required columns ('Name', 'University' or 'Affiliation')
3. **Check File Size**: Keep files under 50MB for best performance
4. **Data Quality**: Clean your data before upload to ensure accurate results

### **Error Handling & Retry Logic**
The application now includes automatic retry mechanisms for:
- **API Calls**: Automatic retries with exponential backoff for OpenAI and Google Serper APIs
- **Web Scraping**: Enhanced error recovery for network timeouts and connection issues
- **File Processing**: Better error messages and recovery options for file parsing issues

---

## **Recent Updates & Improvements**

### **Enhanced Reliability**
- ✅ **API Retry Logic**: Automatic retries for failed API calls with intelligent backoff
- ✅ **Memory Management**: Improved WebDriver cleanup to prevent memory leaks
- ✅ **Error Handling**: More specific error messages for easier troubleshooting

### **Security Enhancements**
- ✅ **File Validation**: Comprehensive security checks for all uploaded files
- ✅ **Input Sanitization**: Enhanced validation of all user inputs
- ✅ **Safe Processing**: Protected against malicious file uploads and content

### **User Experience Improvements**
- ✅ **Better Error Messages**: More descriptive feedback for failed operations
- ✅ **Improved Interface**: Enhanced text areas and form layouts
- ✅ **Faster Processing**: Optimized performance with better resource management

---

### For more technical documentation, please refer to the GitHub repository.

---

