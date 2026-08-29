// Servidor estatico minimo (sin dependencias) para ver la guia y bajar los STL.
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const RAIZ = path.dirname(fileURLToPath(import.meta.url));
const PUERTO = process.env.PORT ? Number(process.env.PORT) : 4321;
const TIPOS = {
  '.html': 'text/html; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.stl': 'model/stl',
  '.obj': 'model/obj',
  '.zip': 'application/zip',
  '.svg': 'image/svg+xml',
  '.py': 'text/plain; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
};

http.createServer((req, res) => {
  let ruta;
  try {
    ruta = decodeURIComponent((req.url || '/').split('?')[0]);
  } catch {
    res.writeHead(400).end('mala url');
    return;
  }
  if (ruta === '/') ruta = '/index.html';
  const abs = path.join(RAIZ, path.normalize(ruta));
  if (!abs.startsWith(RAIZ)) {
    res.writeHead(403).end('no');
    return;
  }
  fs.stat(abs, (err, st) => {
    if (err || !st.isFile()) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }).end('no existe: ' + ruta);
      return;
    }
    const ext = path.extname(abs).toLowerCase();
    res.writeHead(200, {
      'content-type': TIPOS[ext] || 'application/octet-stream',
      'content-length': st.size,
      'cache-control': 'no-store',
    });
    fs.createReadStream(abs).pipe(res);
  });
}).listen(PUERTO, '0.0.0.0', () => {
  console.log('servidor del estadio en http://0.0.0.0:' + PUERTO);
});
