@echo off
echo Adding Web version files...
git add web/
git add core/ui/
git add core/backend/
git add *.py
git add *.md
git add requirements*.txt

echo Committing changes...
git commit -m "Add Web version with complete AI integration

- Web-based UI with HTML5/CSS3/JavaScript
- Real AI avatar integration with DeepSeek
- Event system with building interactions
- MBTI-based decision making
- Perfect Chinese font support
- Cross-platform compatibility
- Zero installation required"

echo Pushing to GitHub...
git push origin main

echo Done!
pause