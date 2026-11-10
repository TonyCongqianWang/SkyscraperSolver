// GitHub's latest stable release plus the most recently published prerelease.
function selectVersions(releases, stable) {
  const prerelease = releases.filter(release =>
    !release.draft && release.prerelease && release.published_at
  ).sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at))[0];
  const versions = [];
  if (stable) versions.push(version(stable, "release"));
  if (prerelease && (!stable ||
      Date.parse(prerelease.published_at) > Date.parse(stable.published_at))) {
    versions.push(version(prerelease, "prerelease"));
  }
  if (!versions.length) throw new Error("No published release or prerelease is available");
  return { default: versions[0].id, versions };
}

function version(release, id) {
  return {
    id, tag: release.tag_name, prerelease: release.prerelease,
    published_at: release.published_at, path: `${id}/solver.js`,
  };
}

module.exports = { selectVersions };
