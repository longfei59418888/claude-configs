const fs = require("fs");
const os = require("os");
const path = require("path");

const packageRoot = path.resolve(__dirname, "..");
const sourceDir = path.join(packageRoot, "skills", "get-skill");
const installHome =
  process.env.GET_SKILL_INSTALL_HOME ||
  process.env.CLAUDE_CONFIGS_INSTALL_HOME ||
  os.homedir();

const destinations = [
  path.join(installHome, ".agent", "skills", "get-skill"),
  path.join(installHome, ".claude", "skills", "get-skill"),
];

function copyDirectory(source, destination) {
  fs.mkdirSync(destination, { recursive: true });

  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    const sourcePath = path.join(source, entry.name);
    const destinationPath = path.join(destination, entry.name);

    if (entry.isDirectory()) {
      copyDirectory(sourcePath, destinationPath);
      continue;
    }

    if (entry.isFile()) {
      fs.copyFileSync(sourcePath, destinationPath);
    }
  }
}

if (!fs.existsSync(path.join(sourceDir, "SKILL.md"))) {
  throw new Error(`Missing get-skill source at ${sourceDir}`);
}

for (const destination of destinations) {
  copyDirectory(sourceDir, destination);
  console.log(`Installed get-skill to ${destination}`);
}
