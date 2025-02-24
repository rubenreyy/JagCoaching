import React, { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Progress } from '../ui/Progress'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../ui/Accordion'
import { AlertCircle, CheckCircle2, File, Upload as UploadIcon, X } from 'lucide-react'
import AIAnalyzing from '../loading/AIAnalyzing'

const Upload = ({ setCurrentPage }) => {
  const [files, setFiles] = useState([])
  const [uploadProgress, setUploadProgress] = useState({})
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleFileChange = (event) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files)
      setFiles((prevFiles) => [...prevFiles, ...newFiles])
      newFiles.forEach((file) => {
        simulateUpload(file.name)
      })
    }
  }

  const simulateUpload = (fileName) => {
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      setUploadProgress((prev) => ({ ...prev, [fileName]: progress }))
      if (progress >= 100) {
        clearInterval(interval)
      }
    }, 500)
  }

  const removeFile = (fileName) => {
    setFiles((prevFiles) => prevFiles.filter((file) => file.name !== fileName))
    setUploadProgress((prev) => {
      const newProgress = { ...prev }
      delete newProgress[fileName]
      return newProgress
    })
  }

  const isUploadComplete = Object.values(uploadProgress).every((progress) => progress === 100)

  const handleAnalyze = () => {
    setIsAnalyzing(true)
  }

  const handleAnalysisComplete = useCallback(() => {
    setIsAnalyzing(false)
    setCurrentPage('feedback')
  }, [setCurrentPage])

  return (
    <>
      {isAnalyzing && <AIAnalyzing onComplete={handleAnalysisComplete} />}
      <div className="max-w-[1280px] mx-auto py-20 flex flex-col gap-7">
        <Card>
          <CardHeader>
            <CardTitle>Upload Your Presentation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-[#EEEEEE] rounded-2xl p-12 text-center">
              <UploadIcon className="mx-auto h-12 w-12 text-[#8E8E8E]" />
              <p className="mt-2 text-xl font-mono text-[#030303]">
                Drag and drop your files here, or
              </p>
              <label
                htmlFor="file-upload"
                className="mt-4 cursor-pointer inline-flex items-center px-8 py-3 text-white bg-[#030303] rounded-full font-mono font-semibold hover:bg-primary transition-colors"
              >
                Browse Files
              </label>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                className="sr-only"
                onChange={handleFileChange}
                multiple
              />
              <p className="mt-4 text-sm font-mono text-[#8E8E8E]">
                Supported formats: .mp4, .mov, .avi, .webm, .pdf, .ppt, .pptx (Max 500MB)
              </p>
            </div>
          </CardContent>
        </Card>

        {files.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Files</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="divide-y divide-[#EEEEEE]">
                {files.map((file, index) => (
                  <li key={index} className="py-4 flex items-center justify-between">
                    <div className="flex items-center">
                      <File className="h-5 w-5 text-[#8E8E8E] mr-3" />
                      <span className="text-lg font-mono text-[#030303]">{file.name}</span>
                    </div>
                    <div className="flex items-center">
                      {uploadProgress[file.name] === 100 ? (
                        <CheckCircle2 className="h-5 w-5 text-primary mr-2" />
                      ) : (
                        <Progress value={uploadProgress[file.name]} className="w-24 mr-2" />
                      )}
                      <button 
                        onClick={() => removeFile(file.name)}
                        className="p-1 hover:text-primary transition-colors"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        <div className="relative group">
          <button 
            onClick={handleAnalyze}
            className={`w-full px-8 py-3 rounded-full font-mono font-semibold transition-colors
              ${isUploadComplete && files.length > 0
                ? 'bg-[#030303] text-white hover:bg-primary'
                : 'bg-[#EEEEEE] text-[#8E8E8E] cursor-not-allowed'
              }`}
            disabled={!isUploadComplete || files.length === 0}
          >
            {isUploadComplete ? "Analyze My Presentation" : "Processing..."}
          </button>
          {(!isUploadComplete || files.length === 0) && (
            <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-[#030303] text-white px-4 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap font-mono">
              Upload file first
            </div>
          )}
        </div>

        <Card>
          <CardContent className="p-0">
            <Accordion type="single" collapsible>
              <AccordionItem value="guidelines">
                <AccordionTrigger>Upload Guidelines & Help</AccordionTrigger>
                <AccordionContent>
                  <ul className="list-disc list-inside space-y-2 font-mono text-[#030303]">
                    <li>Supported file formats: .mp4, .mov, .avi, .webm, .pdf, .ppt, .pptx</li>
                    <li>Maximum file size: 500MB per file</li>
                    <li>For best results, ensure your video has clear audio and your slides are legible</li>
                    <li>If your file fails to upload, try reducing its size or using a different format</li>
                  </ul>
                  <button className="mt-6 px-6 py-2 border-2 border-[#EEEEEE] rounded-full font-mono font-semibold text-[#030303] hover:bg-primary hover:text-white hover:border-primary transition-colors flex items-center">
                    <AlertCircle className="mr-2 h-4 w-4" />
                    Contact Support
                  </button>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
      </div>
    </>
  )
}

export default Upload 