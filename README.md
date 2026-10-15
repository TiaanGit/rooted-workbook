# Rooted Workbook Platform
**Life Church Waterfall**  
A clear path of discipleship for new believers and new members.

## Purpose
This is an original online workbook platform designed for Life Church Waterfall.  
It provides an 8-module discipleship pathway covering foundational Christian beliefs and practices.

**Important:** This is an original resource. Do not copy content from commercial programs such as "Experience Rooted". All teaching content should be developed by Life Church elders and writers based on Scripture.

## Features
- User login (admin and regular users)
- 8-module structure with sections, key scriptures, and reflection questions
- Progress tracking and personal notes
- Admin panel to edit content directly in the browser
- Export content to Markdown (ready for printing / PDF conversion)
- Branded with Life Church and Rooted logos

## Demo Credentials
- **Admin:** username `admin` / password `rooted2026`
- **User:** username `demo` / password `demo123`

**Change these passwords before any real use.**

## How to Run Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. Open the URL shown in the terminal (usually http://localhost:8501)

## Content Development
- Content is stored in `content/modules.yaml`
- Admins can edit via the Admin Panel inside the app
- Elders and writers can expand the placeholder sections with original teaching, illustrations, and applications
- Once content is complete, use the "Generate Printable Summary" button to export everything for print production

## Deployment Options
- **Local / Church computer:** Run with Streamlit as above
- **Streamlit Community Cloud:** Free hosting (push to GitHub and connect)
- **Church server:** Deploy with Docker or a simple VPS
- **Future:** Can be extended with proper database (PostgreSQL), email auth, and PDF generation

## Module Overview (Skeleton)
1. The Gospel: Salvation by Grace Through Faith
2. Identity in Christ
3. The Authority of Scripture
4. Prayer: Talking with the Father
5. The Holy Spirit
6. The Church: Doing Life Together
7. Growing in Christ: Spiritual Disciplines
8. Released: Making Disciples

These align with Life Church's vision: **Rooted • Renewed • Released**.

## Next Steps
1. Review and adjust the module titles/structure with elders
2. Begin writing original content for each section
3. Test with a small group of new believers
4. Develop a polished printable version once content is complete
5. Consider adding video embeds, quizzes, or group discussion prompts

---
*Built for Life Church Waterfall. Keep the content original, biblical, and focused on making disciples that make disciples.*
