"use client";

import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Loader2 } from "lucide-react";

interface ProcessingOverlayProps {
  isOpen: boolean;
  progress: number;
  status: string;
}

export function ProcessingOverlay({ isOpen, progress, status }: ProcessingOverlayProps) {
  return (
    <Dialog open={isOpen} modal>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="sr-only">Processing Request</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col items-center justify-center py-8 space-y-4">
          <div className="relative">
            <Loader2 className="w-12 h-12 animate-spin text-primary" />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-sm font-medium text-primary">
                {Math.round(progress)}%
              </span>
            </div>
          </div>
          
          <div className="text-center space-y-2">
            <h3 className="text-lg font-semibold">Processing Your Request</h3>
            <p className="text-sm text-muted-foreground">{status}</p>
          </div>
          
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <p className="text-xs text-muted-foreground text-center">
            Please wait while we prepare your files. Do not close this window.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
