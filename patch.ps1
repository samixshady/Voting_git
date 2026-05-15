$content = Get-Content E:\Projects\Voting_git\voting\templates\voting\login.html -Raw
$new_content = $content -replace '</div>\s*</div>\s*{% endblock content %}', '</div>
        
        <div class="login-box-body" style="margin-top: 20px;">
            <h4 class="text-center">Demo Accounts</h4>
            <div class="row">
                <div class="col-xs-6">
                    <strong>Voter 1</strong><br>
                    Email: demovoter1@demo.com<br>
                    Pass: demo123<br>
                    <button class="btn btn-info btn-xs btn-block" style="margin-top:5px;" onclick="demoLogin(''demovoter1@demo.com'', ''demo123'')">Click to Login</button>
                </div>
                <div class="col-xs-6">
                    <strong>Voter 2</strong><br>
                    Email: demovoter2@demo.com<br>
                    Pass: demo123<br>
                    <button class="btn btn-info btn-xs btn-block" style="margin-top:5px;" onclick="demoLogin(''demovoter2@demo.com'', ''demo123'')">Click to Login</button>
                </div>
            </div>
            
            <div class="row" style="margin-top: 15px;">
                <div class="col-xs-12">
                   <strong>Admin (Custom)</strong><br>
                   Email: admin@admin.com<br>
                   Pass: admin<br>
                   <button class="btn btn-danger btn-xs btn-block" style="margin-top:5px;" onclick="demoLogin(''admin@admin.com'', ''admin'')">Click to Login (Admin)</button>
                </div>
            </div>
        </div>
        
        <script>
        function demoLogin(email, password) {
            document.querySelector(''input[name="email"]'').value = email;
            document.querySelector(''input[name="password"]'').value = password;
            document.querySelector(''form'').submit();
        }
        </script>
    </div>

{% endblock content %}'
Set-Content E:\Projects\Voting_git\voting\templates\voting\login.html -Value $new_content
