#!/bin/bash

# Auto-fix missing frontmatter fields in skill SKILL.md files
# Adds sensible defaults before closing --- marker, preserving existing formatting

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TODAY="2026-05-29"
FIXED=0
SKIPPED=0

echo "Fixing missing frontmatter fields..."
echo ""

ruby << 'RUBY_SCRIPT'
require 'yaml'

TODAY = "2026-05-29"
fixed = 0
skipped = 0

Dir.glob("*-*/SKILL.md").sort.each do |skill_file|
  skill_name = File.dirname(skill_file)
  content = File.read(skill_file)

  # Extract frontmatter text (between --- markers)
  unless content =~ /^---\n(.*?)\n---\n/m
    puts "ERROR: #{skill_name}: No valid frontmatter"
    next
  end

  fm_text = $1
  body = content.sub(/^---\n.*?\n---\n/m, '')

  # Parse to check what's missing
  begin
    fm = YAML.unsafe_load(fm_text)
  rescue => e
    puts "ERROR: #{skill_name}: Invalid YAML - #{e.message}"
    next
  end

  # Check what's missing
  missing = []
  missing << "status" unless fm.key?("status")
  missing << "last_reviewed" unless fm.key?("last_reviewed")
  missing << "version" unless fm.key?("version")
  missing << "user-invocable" unless fm.key?("user-invocable")
  missing << "impact" unless fm.key?("impact")

  if missing.empty?
    skipped += 1
    next
  end

  # Build additions with proper formatting
  additions = ""
  additions += "status: active\n" if missing.include?("status")
  additions += "last_reviewed: #{TODAY}\n" if missing.include?("last_reviewed")
  additions += "version: \"1.0.0\"\n" if missing.include?("version")
  additions += "user-invocable: true\n" if missing.include?("user-invocable")
  additions += "impact: \"low\"\n" if missing.include?("impact")

  # Insert before closing --- (preserve original formatting)
  new_fm = fm_text.rstrip + "\n" + additions
  new_content = "---\n#{new_fm}---\n#{body}"

  File.write(skill_file, new_content)
  puts "Fixed: #{skill_name} (added: #{missing.join(', ')})"
  fixed += 1
end

puts ""
puts "Summary:"
puts "  Fixed:   #{fixed} skills"
puts "  Skipped: #{skipped} skills (already complete)"
puts ""
puts "Verify with: ./scripts/audit-skills.sh"
RUBY_SCRIPT

