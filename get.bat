git checkout master
git pull

python leetcode.py
python leetcode-cn.py

git status
echo "??Ҫ???͵? Git ?ֿ?"
pause
git add .
git commit -m "update"
git gc

git remote add origin https://github.com/coder-xiaomo/leetcode-problemset
git push origin

git remote add github https://github.com/coder-xiaomo/leetcode-problemset
git push github

pause