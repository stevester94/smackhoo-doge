# KNOWN PROBLEMS
# - Breaks when files have spaces in them
# - Doesn't ignore files in the dockerignore if they are added or deleted

image_name := smackhoo-doge
registry_url := ssmackey
prod_container_name := doge-prod

.PHONY: all image save push

image: .image_marker

# Modify Me!
run-local: image
	docker run -t --rm -p5984:5984 ${image_name} ./server.py 5984

# Modify Me!
run-prod: image push
	ssh dev.ssmackey.com "docker kill doge-prod"
	ssh dev.ssmackey.com "docker rm doge-prod"
	ssh dev.ssmackey.com "docker pull ${registry_url}/${image_name}"
	ssh dev.ssmackey.com "docker run --name doge-prod -td --network=host --restart always ${registry_url}/${image_name} ./server.py 5984"

# What this madness does:
#
# .image_marker: A listing of files that were used for the previous build (this hangs around but should not be checked in)
# .thisFileWillNeverExistEver: A temporary listing of current files
#
# The two files will be compared. If there are any differences in the files (IE a file was deleted or added), the script
# will touch the Makefile (this is important in the next step)
# .thisFileWillNeverExistEver is then deleted (it's no longer needed)
#
# In the second step of the script, all files that aren't in dockerignore are found, and used as the pre-reqs for .image_marker
# If any files are newer than .image_marker the recipe will be invoked.
# If the makefile was touched in the first step, the recipe will be invoked.
.image_marker: $(shell find . -mindepth 1 | grep -v .thisFileWillNeverExistEver > .thisFileWillNeverExistEver; \
	if ! cmp -s .thisFileWillNeverExistEver .image_marker; then \
		touch Makefile; \
	fi; \
	rm .thisFileWillNeverExistEver; \
	if test -f .dockerignore; then \
		find . -mindepth 1 | grep -v -f .dockerignore | grep -v .image_marker; \
	else \
		find . -mindepth 1 | grep -v .image_marker; \
	fi )

	docker build -t ${image_name} .
	@find . -mindepth 1 > .image_marker

push: image
	docker tag ${image_name} ${registry_url}/${image_name}
	docker push ${registry_url}/${image_name}

save: image
	docker save ${image_name} > ${image_name}.tar

clean:
	rm -f .image_marker
	docker rmi -f ${image_name}
	docker rmi -f ${registry_url}/${image_name}