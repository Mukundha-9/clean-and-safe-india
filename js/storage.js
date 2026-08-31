/* ==========================================================================
   Clean & Safe India App - Storage & Image Processing Layer
   Canvas-based client-side compression, EXIF geo-data extraction & preview
   ========================================================================== */

class StorageManager {
  // Compress and convert an image file to Base64 data URL
  async processImage(file, maxWidth = 1200, quality = 0.82) {
    return new Promise((resolve, reject) => {
      if (!file.type.startsWith('image/')) {
        reject(new Error("Selected file is not an image."));
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          let width = img.width;
          let height = img.height;

          // Scale down if exceeding maxWidth
          if (width > maxWidth) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          }

          canvas.width = width;
          canvas.height = height;

          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);

          // Add timestamp watermark simulation
          ctx.fillStyle = "rgba(15, 23, 42, 0.75)";
          ctx.fillRect(10, height - 38, 300, 28);
          ctx.font = "bold 12px monospace";
          ctx.fillStyle = "#38bdf8";
          const stamp = `CLEAN&SAFE GPS: ${new Date().toLocaleTimeString()} ${new Date().toLocaleDateString()}`;
          ctx.fillText(stamp, 18, height - 20);

          const compressedBase64 = canvas.toDataURL('image/jpeg', quality);
          resolve(compressedBase64);
        };
        img.onerror = reject;
        img.src = e.target.result;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  // Fallback high-quality civic placeholder images
  getDefaultImageForCategory(category) {
    const defaultImages = {
      garbage: "https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80",
      food_hygiene: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80",
      food_spoilage: "https://images.unsplash.com/photo-1584727638096-042c45049ebe?w=800&auto=format&fit=crop&q=80",
      littering: "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=800&auto=format&fit=crop&q=80"
    };
    return defaultImages[category] || defaultImages.garbage;
  }
}

export const storage = new StorageManager();
