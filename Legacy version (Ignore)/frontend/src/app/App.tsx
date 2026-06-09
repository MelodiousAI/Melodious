import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { Footer } from '../components/Footer'
import { Navbar } from '../components/Navbar'
import { HomePage } from '../pages/HomePage'
import { LibraryPage } from '../pages/LibraryPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { UploadPage } from '../pages/UploadPage'
import { WorkspacePage } from '../pages/WorkspacePage'

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen flex-col">
        <Navbar />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/samples" element={<LibraryPage />} />
            <Route path="/workspace/:sampleId" element={<WorkspacePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </BrowserRouter>
  )
}

export default App
