// Utility functions for creating and downloading zip files

interface ZipFile {
  name: string;
  blob: Blob;
}

export async function createZipFile(files: ZipFile[], zipName: string): Promise<void> {
  // Import JSZip dynamically to avoid bundle size issues
  const JSZip = (await import('jszip')).default;
  
  const zip = new JSZip();
  
  // Add all files to the zip
  files.forEach(file => {
    zip.file(file.name, file.blob);
  });
  
  // Generate the zip file
  const zipBlob = await zip.generateAsync({ type: 'blob' });
  
  // Create download link
  const url = URL.createObjectURL(zipBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = zipName;
  link.target = '_blank';
  
  // Trigger download
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Clean up
  URL.revokeObjectURL(url);
}

export function getZipStatusMessage(progress: number): string {
  if (progress < 10) return "Preparing files...";
  if (progress < 80) return "Downloading clips...";
  if (progress < 95) return "Creating zip file...";
  if (progress < 100) return "Finalizing download...";
  return "Complete!";
}
