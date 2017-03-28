Function.prototype.method = function (name, func) {
    this.prototype[name] = func;
    return this;
};

Handlebars.registerHelper('stripLinks', function(context, options) {
    var $context = $("<div>" + context +"</div>");
    $context.find("a").contents().unwrap();
    return $context.html();
});

function ManualParser(url) {
    this.url = url;
    this.manual = {};

    this.templateToc = Handlebars.compile($("#template-toc").html());
    this.templateTocSide = Handlebars.compile($("#template-toc-side").html());
    this.templateChapter = Handlebars.compile($("#template-chapter").html());
    this.templateArticle = Handlebars.compile($("#template-article").html());
}
ManualParser.method("fetchManual", function() {
    var self = this;

    $.get(this.url + "manual.json", function(data, status, jqXHR) {
        self.parseManual(data);
    });

    return this;
});
ManualParser.method("parseManual", function(data) {
    var self = this;

    self.manual.title = data.title;
    self.manual.uuid = data.uuid;
    self.manual.chapters = [];

    $.each(data.chapters, function(indexChapter, chapter) {
        var newChapter = {};
        newChapter.uuid = chapter.uuid;
        newChapter.title = chapter.title;
        newChapter.number = indexChapter + 1;
        
        newChapter.articles = [];
      	$.each(chapter.articles, function(indexArticle, article) {
      		newChapter.articles[indexArticle] = {uuid: article.id, chapter: indexChapter + 1, chapterOrder: indexArticle + 1, numArticles: chapter.articles.length};
      		if (indexArticle == 0) {
            newChapter.articles[indexArticle].activePage = true;
          }
      	});
        
        self.manual.chapters.push(newChapter);
        $("#manual").trigger("onAddNewChapter", {chapter: newChapter.number, numArticles: newChapter.articles.length});
    });

    $("#table-of-contents").append(self.templateToc(self.manual));

    $("#table-of-contents-header").append(self.templateTocSide(self.manual)).trigger("tocDrawn");

    $.each(self.manual.chapters, function(indexChapter, chapter) {
        $("#manual .manual-interior").append(self.templateChapter(chapter));
        $.each(chapter.articles, function(indexArticle, article) {
            self.parseArticle(article);
        });
    });

    return this;
});
ManualParser.method("parseArticle", function(article) {
    var self = this;

    $.get(this.url + "articles/" + article.uuid + ".json", function(data, status, jqXHR) {
        article.description = data.description;
        article.title = data.title;
        article.steps = data.steps;
        if (article.steps) {
					$.each(article.steps, function(index, step) {
							if (step.media.fullsize != null) {
								// Rebuild the relative URL
								step.media.fullsize.relative_filename = self.url + "images/" + article.uuid + "/" + step.media.fullsize.relative_filename.split('/').pop();
								step.parsedImageEncoded = encodeURIComponent(step.media.fullsize.relative_filename);
							}
					});
        }

        var $chapter = $("#chapter-" + article.chapter + " .pages-interior");
        var inserted = false;
        for (var i = article.chapterOrder + 1; !inserted && i <= article.numArticles; i++) {
            var $steps = $(".article-" + article.chapter + "-" + i, $chapter);
            if ($steps.length) {
                $steps.first().before(self.templateArticle(article));
                inserted = true;
            }
        }

        if (!inserted) {
            $chapter.append(self.templateArticle(article));
        }

        $("#manual").trigger("onAddNewArticle", {chapter: article.chapter});
    });

    return this;
});

ManualParser.method("getNumberOfChapters", function() {
    return this.manual.chapters.length || 0;
});
ManualParser.method("getNumberOfArticlesForChapter", function(chapter) {
    return this.manual.chapters[chapter].articles.length || 0;
});


$(document).ready(function () {
    /*
     * Chapter selection, prev/next paging
     */
    function insertPageNumbers(){
        var $currentChapter = $('.active-chapter');

        var total = $(".step-container", $currentChapter).length;
        $(".total-pages", $currentChapter).html(total);

        $(".current-page", $currentChapter).each(function(index) {
            $(this).html(Math.floor(index/2 + 1));
        });
    }

    function showHidePrevNext() {
        var $currentStep = $('.active-chapter').find('.active-page');

        if (isFirstChapter($currentStep) && isFirstStep($currentStep)) {
            $currentStep.closest('.chapter').find('.prev').css({visibility: "hidden"});
        } else {
            $currentStep.closest('.chapter').find('.prev').css({visibility: "visible"});
        }
        if (isLastChapter($currentStep) && isLastStep($currentStep)) {
            $currentStep.closest('.chapter').find('.next').css({visibility: "hidden"});
        } else {
            $currentStep.closest('.chapter').find('.next').css({visibility: "visible"});
        }
    }

    function showHideTocHeaderButtons() {
        var $chapters = $("#table-of-contents-header .switch-area");
        if ($chapters.filter(":visible").first().data("target") == $chapters.first().data("target")) {
            $("#table-of-contents-prev").hide();
        } else {
            $("#table-of-contents-prev").show();
        }
        if ($chapters.filter(":visible").last().data("target") != $chapters.last().data("target")) {
            $("#table-of-contents-next").show();
        } else {
            $("#table-of-contents-next").hide();
        }
    }

	function switchChapters(chapterId, options) {
		options = options || {};
		$('.active-chapter').removeClass('active-chapter');
		$('[data-target="' + chapterId + '"]').addClass('active-chapter');

		$('.manual-area').hide();
		hideModal();

		$(chapterId).addClass('active-chapter').show(0, function () {
			$("#table-of-contents-header").show();
			if (options.showFirstPage) {
				$(this).find('.page').removeClass('active-page').first().addClass('active-page');
			}
			if (options.showLastPage) {
				$(this).find('.page').removeClass('active-page').last().addClass('active-page');
			}
			insertPageNumbers();
			showHidePrevNext();
			showHideTocHeaderButtons();
		});
	}

	function isLastChapter($currentStep) {
		return !($currentStep.closest(".chapter").next(".chapter").length > 0);
	}
	function isFirstChapter($currentStep) {
		return !($currentStep.closest(".chapter").prev(".chapter").length > 0);
	}
	function isFirstStep($currentStep) {
		return !($currentStep.prev('.page').length > 0);
	}
	function isLastStep($currentStep) {
		return !($currentStep.next('.page').length > 0);
	}

	function hideModal() {
		$('#modal').fadeOut('fast');
	}

    $(document).on('click', '.switch-area', function () {
		switchChapters($(this).data('target'));
    });

    $(document).on('click', '.next', function (e) {
        e.preventDefault();
		var $currentPage = $('.active-chapter').find('.active-page');

		if (!isLastStep($currentPage)) {
			$currentPage.removeClass('active-page')
				.next().addClass('active-page');
			hideModal();
			showHidePrevNext();
		} else {
			var $nextChapter = $currentPage.closest(".chapter").next(".chapter");
			switchChapters('#' + $nextChapter.attr("id"), {showFirstPage: true});
		}
    });

    $(document).on('click', '.prev', function (e) {
        e.preventDefault();
        var $currentPage = $('.active-chapter').find('.active-page');

		if (!isFirstStep($currentPage)) {
			$currentPage.removeClass('active-page')
				.prev().addClass('active-page');
			hideModal();
			showHidePrevNext();
		} else {
			var $prevChapter = $currentPage.closest(".chapter").prev(".chapter");
			switchChapters('#' + $prevChapter.attr("id"), {showLastPage: true});
		}
    });

    $(document).on('click', "#back-to-toc", function(e) {
        e.preventDefault();
		hideModal();
        $('.active-chapter').removeClass('active-chapter');
        $('.manual-area').hide();
        $('#table-of-contents-header').hide();
        $('#table-of-contents').show();
    });

    $(document).on("tocDrawn", function() {
        var $chapters = $("#table-of-contents-header .switch-area");

        $chapters.qtip({
            position: {
                my: 'top center',
                at: 'bottom center',
                viewport: $(window),
                adjust: {
                    method: "shift none"
                }
            },
            style: { classes: 'tooltip' }
        });

        $chapters.each(function(index) {
            if (index >= 13) {
                $(this).hide();
            }
        });

        $("#table-of-contents-next").click(function(e) {
            e.preventDefault();
            $chapters.filter(":visible").first().hide();
            $chapters.filter(":visible").last().next().show();
            showHideTocHeaderButtons();

        });
        $("#table-of-contents-prev").click(function(e) {
            e.preventDefault();
            $chapters.filter(":visible").first().prev().show();
            $chapters.filter(":visible").last().hide();
            showHideTocHeaderButtons();
        });
    });

    var chapterList = {};
    var loadedChapterList = {};
    $("#manual").on("onAddNewChapter", function(event, data) {
        chapterList[data.chapter] = data.numArticles;
        loadedChapterList[data.chapter] = 0;
    });

    $("#manual").on("onAddNewArticle", function(event, data) {
        loadedChapterList[data.chapter]++;
        if (loadedChapterList[data.chapter] === chapterList[data.chapter]) {
            var $chapter = $("#chapter-" + data.chapter);
            $(".chapter-loading", $chapter).remove();
            if ($chapter.hasClass("active-chapter")) {
                $chapter.find('.active-page').first().show(0);
                $("#table-of-contents-header").show();
                insertPageNumbers();
                showHidePrevNext();
                showHideTocHeaderButtons();
            }
        }
    });
});