const MAX_UPLOAD_IMAGE_BYTES = 850 * 1024;
const COMPRESSION_QUALITIES = [82, 72, 62, 52, 42, 32, 24];

function getFileInfo(filePath) {
  const safePath = String(filePath || "").trim();
  if (!safePath) {
    return Promise.reject(new Error("未选择图片"));
  }
  return new Promise((resolve, reject) => {
    wx.getFileInfo({
      filePath: safePath,
      success: resolve,
      fail(error) {
        reject(error || new Error("图片读取失败"));
      }
    });
  });
}

function compressImage(filePath, quality) {
  return new Promise((resolve, reject) => {
    wx.compressImage({
      src: filePath,
      quality,
      success(res) {
        const nextPath = String((res && res.tempFilePath) || "").trim();
        if (!nextPath) {
          reject(new Error("图片压缩失败"));
          return;
        }
        resolve(nextPath);
      },
      fail(error) {
        reject(error || new Error("图片压缩失败"));
      }
    });
  });
}

async function compressImageForUpload(filePath, options = {}) {
  const maxBytes = Number(options.maxBytes || MAX_UPLOAD_IMAGE_BYTES);
  let currentPath = String(filePath || "").trim();
  let currentInfo = await getFileInfo(currentPath);
  const originalSize = Number(currentInfo.size || 0);

  if (originalSize > 0 && originalSize <= maxBytes) {
    return {
      path: currentPath,
      size: originalSize,
      originalSize,
      compressed: false
    };
  }

  for (const quality of COMPRESSION_QUALITIES) {
    const nextPath = await compressImage(currentPath, quality);
    const nextInfo = await getFileInfo(nextPath);
    const nextSize = Number(nextInfo.size || 0);
    currentPath = nextPath;
    currentInfo = nextInfo;
    if (nextSize > 0 && nextSize <= maxBytes) {
      return {
        path: nextPath,
        size: nextSize,
        originalSize,
        compressed: true
      };
    }
  }

  const finalSize = Number(currentInfo.size || 0);
  if (finalSize > 0 && finalSize <= maxBytes) {
    return {
      path: currentPath,
      size: finalSize,
      originalSize,
      compressed: true
    };
  }

  throw new Error("图片仍然过大，请换一张更清晰但体积更小的图片");
}

module.exports = { MAX_UPLOAD_IMAGE_BYTES, compressImageForUpload };
