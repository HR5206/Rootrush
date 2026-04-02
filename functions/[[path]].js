export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Handle API requests
    if (url.pathname.startsWith('/api/') || 
        url.pathname.startsWith('/inputs') ||
        url.pathname.startsWith('/results') ||
        url.pathname.startsWith('/insights')) {
      return handleBackendRequest(request, env);
    }

    // Handle static files
    if (url.pathname.match(/\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2)$/)) {
      return handleStaticAsset(request, env);
    }

    // Default: serve from backend or static
    return handleBackendRequest(request, env);
  }
};

async function handleBackendRequest(request, env) {
  const backendURL = env.BACKEND_URL;
  
  if (!backendURL) {
    return new Response('Backend URL not configured', { status: 500 });
  }

  const url = new URL(request.url);
  const targetURL = new URL(url.pathname + url.search, backendURL);

  try {
    const response = await fetch(new Request(targetURL, {
      method: request.method,
      headers: request.headers,
      body: request.body,
      cf: {
        cacheEverything: true,
        cacheTtl: 300, // 5 minutes
      }
    }));

    // Add security headers
    const newHeaders = new Headers(response.headers);
    newHeaders.set('X-Content-Type-Options', 'nosniff');
    newHeaders.set('X-Frame-Options', 'DENY');
    newHeaders.set('X-XSS-Protection', '1; mode=block');
    newHeaders.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });
  } catch (error) {
    console.error('Backend request error:', error);
    return new Response('Backend service unavailable', { status: 503 });
  }
}

async function handleStaticAsset(request, env) {
  const url = new URL(request.url);
  const backendURL = env.BACKEND_URL;

  if (!backendURL) {
    return new Response('Not found', { status: 404 });
  }

  const targetURL = new URL(url.pathname + url.search, backendURL);

  try {
    const response = await fetch(targetURL, {
      cf: {
        cacheEverything: true,
        cacheTtl: 86400, // 24 hours for static assets
      }
    });

    if (response.ok) {
      const headers = new Headers(response.headers);
      headers.set('Cache-Control', 'public, max-age=86400');
      return new Response(response.body, { status: 200, headers });
    }
    
    return response;
  } catch (error) {
    console.error('Static asset request error:', error);
    return new Response('Asset not found', { status: 404 });
  }
}
