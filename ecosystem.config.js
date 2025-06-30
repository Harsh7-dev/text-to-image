module.exports = {
  apps: [
    {
      name: 'text-to-image',
      script: 'python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 3123',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 3123
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3123
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true
    }
  ]
}; 