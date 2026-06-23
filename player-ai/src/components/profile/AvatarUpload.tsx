'use client';

import { useRef, useState, useTransition } from 'react';
import { saveAvatarAction, removeAvatarAction } from '@/lib/actions/profile';

interface AvatarUploadProps {
  currentDataUrl: string | null;
  displayName: string;
  username: string;
}

export default function AvatarUpload({ currentDataUrl, displayName, username }: AvatarUploadProps) {
  const [preview, setPreview] = useState<string | null>(currentDataUrl);
  const [error, setError] = useState('');
  const [isPending, startTransition] = useTransition();
  const inputRef = useRef<HTMLInputElement>(null);

  const initials = (displayName || username).slice(0, 2).toUpperCase();

  function resizeAndEncode(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const url = URL.createObjectURL(file);
      img.onload = () => {
        URL.revokeObjectURL(url);
        const SIZE = 200;
        const canvas = document.createElement('canvas');
        const scale = Math.min(SIZE / img.width, SIZE / img.height);
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
        const ctx = canvas.getContext('2d')!;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL('image/jpeg', 0.75));
      };
      img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('Failed to load image.')); };
      img.src = url;
    });
  }

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    setError('');
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file.');
      return;
    }
    try {
      const dataUrl = await resizeAndEncode(file);
      setPreview(dataUrl);
      startTransition(async () => {
        const result = await saveAvatarAction(dataUrl);
        if (!result.success) setError(result.error ?? 'Upload failed.');
      });
    } catch {
      setError('Could not process image. Please try another file.');
    }
    e.target.value = '';
  }

  function handleRemove() {
    setError('');
    setPreview(null);
    startTransition(async () => {
      const result = await removeAvatarAction();
      if (!result.success) setError(result.error ?? 'Remove failed.');
    });
  }

  return (
    <div className="flex items-center gap-5">
      {/* Avatar circle */}
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={isPending}
        className="relative w-20 h-20 rounded-full overflow-hidden border-2 border-border/50 hover:border-primary/50 transition-colors group shrink-0 cursor-pointer"
        title="Click to change photo"
      >
        {preview ? (
          <img src={preview} alt="Profile" className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-primary/20 text-primary text-xl font-bold">
            {initials}
          </div>
        )}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <span className="text-white text-xs font-semibold">{isPending ? '...' : 'Change'}</span>
        </div>
      </button>

      {/* Controls */}
      <div className="space-y-1.5">
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={isPending}
          className="block text-sm font-semibold text-primary hover:text-primary/80 transition-colors cursor-pointer disabled:opacity-50"
        >
          {isPending ? 'Saving...' : preview ? 'Change photo' : 'Upload photo'}
        </button>
        {preview && !isPending && (
          <button
            type="button"
            onClick={handleRemove}
            className="block text-xs text-muted-foreground hover:text-destructive transition-colors cursor-pointer"
          >
            Remove photo
          </button>
        )}
        <p className="text-xs text-muted-foreground/60">JPG, PNG or WebP · Max 150KB</p>
        {error && <p className="text-xs text-destructive">{error}</p>}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFile}
        className="hidden"
      />
    </div>
  );
}
