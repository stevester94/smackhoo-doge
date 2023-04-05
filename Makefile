image_name := smackhoo-doge
registry_url := ssmackey

.PHONY: all image save push

all: image

image: .image_marker

# This madness finds all files/dirs in top level directory, and does a diff with the files that were saved
# into .image_marker from the previous build. If there are any differences in files then it will touch the Makefile
# which will force this rule to trigger since the Makefile will be newer than the .image_marker
#
# It will also print all files in current directory, ignoring any files that exist in .dockerignore
#
# Note this is actually subtly broken; we want to ignore files in the .dockerignore during our comparison as well.
# It's good enough for now, but when we need this feature it shouldn't be too hard to implement
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
