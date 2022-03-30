git checkout master
git pull

python leetcode.py
python leetcode-cn.py

git status
echo "将要推送到 Git 仓库"
pause
git add .
git commit -m "update"
git gc
git push
pause