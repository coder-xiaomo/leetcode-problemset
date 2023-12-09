git checkout master
git pull
git count-objects -vH

python leetcode.py
python leetcode-cn.py

git status
echo "将要推送到 Git 仓库"
pause
git add .
git commit -m "update"
git gc

git remote add origin https://gitee.com/coder-xiaomo/leetcode-problemset
git push origin

git remote add github https://github.com/coder-xiaomo/leetcode-problemset
git push github

pause