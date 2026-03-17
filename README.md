# Image Forgery Detector

A robust full-stack application for detecting copy-move forgery in digital images, powered by the SIFT (Scale-Invariant Feature Transform) algorithm.  

[Live Demo] - *Insert Link Here*

## Features
- **Upload Image**: Support for common image formats.
- **Forgery Detection**: Leverages advanced computer vision (SIFT) to find identical regions within an image.
- **Visual Results**: Provides tampered region highlights, keypoints mapping, and heatmap generation.
- **AI Explainer**: Get an automated, non-technical explanation of the results.
- **Forensic PDF Reports**: Export comprehensive forensic analysis to a downloadable PDF document.

## Technologies Used
- **Backend:** Python, FastAPI, OpenCV, Uvicorn (Render for deployment)
- **Frontend:** React (Vite), TailwindCSS (Vercel for deployment)

## How to Run Locally

### Backend Setup
1. Open a terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # On Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # On Mac/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```bash
   python main.py
   # Or using uvicorn: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup
1. Open a new terminal and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## How to Use
1. Once both servers are running, open the frontend app in a web browser.
2. **Upload an Image**: Select an image file you want to test for forgery.
3. **View Results**: Explore the different tabs showing original keypoints, matching features, isolated tampered regions, and an error level heatmap.
4. **Use AI Explainer**: Click 'Explain Results' for an AI-generated analysis.
5. **Download Report**: Generate and download a PDF forensic report containing all visual evidence and meta-information.

## Deployment Instructions

1. **Push code to GitHub**: Commit your changes and push the entire repository to GitHub.
2. **Backend (Render)**:
   - Go to [render.com](https://render.com) and create a free account.
   - Click "New Web Service" and connect your GitHub repository.
   - Select the `backend/` folder when asked.
   - Set Build Command to `pip install -r requirements.txt`.
   - Set Start Command to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
   - Click "Deploy".
3. **Frontend (Vercel)**:
   - Go to [vercel.com](https://vercel.com) and create a free account.
   - Click "Add New..." -> "Project" and import your GitHub repository.
   - Framework preset usually auto-detects Vite.
   - Add an Environment Variable: Name: `VITE_BACKEND_URL`, Value: `(Your new Render Backend URL)`.
   - Click "Deploy" and copy your public URL.
