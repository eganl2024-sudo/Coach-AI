'use client';

import React, { useState, useRef } from 'react';
import { Upload, X } from 'lucide-react';
import { uploadReelAction } from '@/lib/actions/reel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function ReelUploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const selectedFile = files[0];
      setFile(selectedFile);
      const nameWithoutExt = selectedFile.name.substring(0, selectedFile.name.lastIndexOf('.')) || selectedFile.name;
      setTitle(nameWithoutExt);
      setError('');
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const selectedFile = files[0];
      setFile(selectedFile);
      const nameWithoutExt = selectedFile.name.substring(0, selectedFile.name.lastIndexOf('.')) || selectedFile.name;
      setTitle(nameWithoutExt);
      setError('');
    }
  };

  const handleClearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
    setTitle('');
    setNotes('');
    setError('');
    setSuccess(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError('Please select a video file.');
      return;
    }
    if (!title.trim() || title.trim().length < 3) {
      setError('Title must be at least 3 characters long.');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess(false);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      formData.append('notes', notes);

      const result = await uploadReelAction(formData);

      if (result.success) {
        setSuccess(true);
        setTimeout(() => {
          setFile(null);
          setTitle('');
          setNotes('');
          setSuccess(false);
          if (fileInputRef.current) {
            fileInputRef.current.value = '';
          }
        }, 2000);
      } else {
        setError(result.error || 'Upload failed.');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setUploading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-card/40 border border-border/40 backdrop-blur-md rounded-xl p-5 shadow-sm">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="video/mp4,video/mov,video/quicktime,video/webm"
        className="hidden"
      />

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-all ${
          dragOver
            ? 'border-primary bg-primary/5 scale-[0.99]'
            : 'border-border/50 hover:border-border/80 hover:bg-secondary/20'
        }`}
      >
        {file ? (
          <div className="flex items-center justify-between w-full max-w-md bg-secondary/35 border border-border/30 rounded-lg p-3">
            <div className="flex flex-col text-left truncate pr-2">
              <span className="text-sm font-semibold text-foreground truncate">{file.name}</span>
              <span className="text-xs text-muted-foreground">{formatSize(file.size)}</span>
            </div>
            <button
              type="button"
              onClick={handleClearFile}
              className="p-1 rounded-full hover:bg-destructive/15 text-muted-foreground hover:text-destructive transition-colors shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center space-y-2">
            <Upload className="w-8 h-8 text-muted-foreground" />
            <div className="text-sm text-foreground">
              Drag your clip here or <span className="text-primary font-medium">click to browse</span>
            </div>
            <div className="text-xs text-muted-foreground">
              MP4, MOV, WebM · Max 50MB
            </div>
          </div>
        )}
      </div>

      {file && (
        <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="space-y-1.5">
            <Label htmlFor="title" className="text-xs font-semibold text-muted-foreground">
              Title <span className="text-destructive">*</span>
            </Label>
            <Input
              id="title"
              type="text"
              required
              placeholder="e.g. Finishing drill — May session"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="bg-secondary/20 border-border/50 text-sm h-9"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="notes" className="text-xs font-semibold text-muted-foreground">
              Notes
            </Label>
            <textarea
              id="notes"
              rows={3}
              placeholder="What were you working on?"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="flex w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-2 text-sm text-foreground shadow-xs placeholder:text-muted-foreground focus-visible:outline-hidden focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 resize-y"
            />
          </div>
        </div>
      )}

      <Button
        type="submit"
        disabled={uploading || !file || success}
        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold h-9"
      >
        {uploading ? 'Uploading...' : 'Upload Clip'}
      </Button>

      {success && (
        <div className="text-emerald-500 text-sm text-center font-medium py-1 animate-pulse">
          ✓ Clip uploaded successfully!
        </div>
      )}

      {error && (
        <div className="text-destructive text-sm text-center font-medium py-1">
          {error}
        </div>
      )}
    </form>
  );
}
