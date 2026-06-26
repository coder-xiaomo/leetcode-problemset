git checkout master
git pull
git count-objects -vH

:: python leetcode.py
python leetcode-cn.py

git status
echo "将要推送到 Git 仓库"
pause
git add .
git commit -m "update"
git gc

@REM git remote add origin https://gitee.com/coder-xiaomo/leetcode-problemset
git remote add origin git@gitee.com:coder-xiaomo/leetcode-problemset.git
git push origin

@REM git remote add github https://github.com/coder-xiaomo/leetcode-problemset
git remote add github git@github.com:coder-xiaomo/leetcode-problemset.git
git push github

pause
