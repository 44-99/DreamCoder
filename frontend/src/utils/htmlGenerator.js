// HTML 生成工具函数
export function generatePreviewHTML(files) {
  // 收集所有 HTML、CSS、JS 文件
  let htmlContent = '';
  let cssContent = '';
  let jsContent = '';

  files.forEach(file => {
    if (file.path.endsWith('.html')) {
      htmlContent = file.content;
    } else if (file.path.endsWith('.css')) {
      cssContent += file.content + '\n';
    } else if (file.path.endsWith('.js')) {
      jsContent += file.content + '\n';
    }
  });

  // 如果没有 HTML 文件，尝试创建一个简单的
  if (!htmlContent && (cssContent || jsContent)) {
    const docType = '<!DOCTYPE html>';
    const htmlStart = '<html>';
    const headStart = '<head>';
    const metaCharset = '<meta charset="UTF-8">';
    const metaViewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0">';
    const title = '<title>游戏预览</title>';
    const headEnd = '</head>';
    const bodyStart = '<body>';
    const appDiv = '<div id="app"></div>';
    const bodyEnd = '</body>';
    const htmlEnd = '</html>';
    
    let html = docType + '\n' + htmlStart + '\n' + headStart + '\n' + 
               metaCharset + '\n' + metaViewport + '\n' + title + '\n';
    
    if (cssContent) {
      html += '<style>\n' + cssContent + '\n</style>\n';
    }
    
    html += headEnd + '\n' + bodyStart + '\n' + appDiv + '\n';
    
    if (jsContent) {
      html += '<script>\n' + jsContent + '\n</script>\n';
    }
    
    html += bodyEnd + '\n' + htmlEnd;
    htmlContent = html;
  }

  // 处理外部文件引用
  if (htmlContent) {
    // 替换外部CSS文件引用为内联样式
    if (cssContent) {
      htmlContent = htmlContent.replace(/<link[^>]*href="[^"]*\.css"[^>]*>/g, '');
      const styleTag = '<style>\n' + cssContent + '\n</style>';
      if (htmlContent.includes('</head>')) {
        htmlContent = htmlContent.replace('</head>', styleTag + '\n</head>');
      } else if (htmlContent.includes('</head')) {
        htmlContent = htmlContent.replace('</head', styleTag + '\n</head');
      } else {
        htmlContent = htmlContent.replace('</head>', styleTag + '\n</head>');
      }
    }
    
    // 替换外部JS文件引用为内联脚本
    if (jsContent) {
      htmlContent = htmlContent.replace(/<script[^>]*src="[^"]*\.js"[^>]*><\/script>/g, '');
      const scriptTag = '<script>\n' + jsContent + '\n</script>';
      if (htmlContent.includes('</body>')) {
        htmlContent = htmlContent.replace('</body>', scriptTag + '\n</body>');
      } else if (htmlContent.includes('</body')) {
        htmlContent = htmlContent.replace('</body', scriptTag + '\n</body');
      } else {
        htmlContent = htmlContent.replace('</body>', scriptTag + '\n</body>');
      }
    }
  }

  // 如果没有HTML内容，创建一个基础HTML框架
  if (!htmlContent && (cssContent || jsContent)) {
    htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏预览</title>
    ${cssContent ? '<style>\n' + cssContent + '\n</style>' : ''}
</head>
<body>
    <div id="app">游戏加载中...</div>
    ${jsContent ? '<script>\n' + jsContent + '\n</script>' : ''}
</body>
</html>`;
  }

  return htmlContent;
}