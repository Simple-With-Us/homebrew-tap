<p><img src="https://raw.githubusercontent.com/Simple-With-Us/Simple-With-Us/main/assets/logos/swu-logo.png" alt="Simple With Us logo" width="96" height="96"></p>

# Homebrew Tap

Casks for Jay Wedgeworth's Mac apps.

## Usage

```bash
brew tap Simple-With-Us/tap https://github.com/Simple-With-Us/homebrew-tap
brew install --cask codecaps
```

`brew install --cask Simple-With-Us/tap/codecaps` does both in one step, without tapping first.

## Casks

| Cask | What It Is |
|---|---|
| [`codecaps`](Casks/codecaps.rb) | [CodeCaps](https://github.com/Simple-With-Us/CodeCaps) — a macOS menu bar monitor for AI quotas and subscription plans, with fleet push and pull |

Every cask here installs a build signed with a Developer ID and notarized by Apple.  Upgrade with `brew upgrade --cask`, and remove with `brew uninstall --cask`.
