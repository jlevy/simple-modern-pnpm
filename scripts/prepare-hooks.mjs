import { spawnSync } from 'node:child_process';

const inGitRepo =
  spawnSync('git rev-parse --git-dir', {
    shell: true,
    stdio: 'ignore',
  }).status === 0;

if (!inGitRepo) {
  console.log(
    'Skipping lefthook install because this directory is not a Git repo yet. Run `git init -b main` and `pnpm prepare` when ready.',
  );
  process.exit(0);
}

const installResult = spawnSync('lefthook install', {
  shell: true,
  stdio: 'inherit',
});

process.exit(installResult.status ?? 1);
